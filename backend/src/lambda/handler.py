import json
import platform
import boto3

from src.game import app
from src.utility.decorator import cors


dynamo_db = boto3.client('dynamodb')


@cors
def hello(event, context):
    msg = app.hello()
    response = {
        "statusCode": 200,
        "body": msg
    }
    return response


@cors
def get_platform(event, context):
    msg = platform.platform()
    response = {
        "statusCode": 200,
        "body": msg
    }
    return response


@cors
def hello_redis(event, context):
    client_info = app.hello_redis()
    response = {
        "statusCode": 200,
        "body": json.dumps(client_info)
    }
    return response


@cors
def hello_db(event, context):
    msg = app.hello_db()
    response = {
        "statusCode": 200,
        "body": msg
    }
    return response


def connect_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    
    query_parameters = event['queryStringParameters']
    battle_id = query_parameters['battleId']
    team_id = query_parameters['teamId']
    nickname = query_parameters['nickname']
    
    dynamo_db.put_item(
        TableName="websocket-connections-jwlee-test",
        Item={
            'connectionID': {'S': connection_id},
            'battleID': {'S': battle_id},
            'teamID': {'S': team_id},
            'nickname': {'S': nickname}
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': "Add connection to DB"})
    }


def disconnect_handler(event, context):
    connection_id = event['requestContext']['connectionId']

    # Find request user's battle id
    response = dynamo_db.scan(
        TableName="websocket-connections-jwlee-test",
        FilterExpression="connectionID = :connection_id",
        ExpressionAttributeValues={":connection_id": {"S": connection_id}},
        ProjectionExpression="battleID,connectionID"
    )['Items']
    battle_id = response[0]['battleID']['S']
    
    dynamo_db.delete_item(
        TableName="websocket-connections-jwlee-test",
        Key={
            'battleID': {'S': battle_id},
            'connectionID': {'S': connection_id}
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': "Delete connection from DB"})
    }


def send_handler(event, context):
    paginator = dynamo_db.get_paginator('scan')
    connections = []    # Contain all items in dynamodb table.
    for page in paginator.paginate(TableName="websocket-connections-jwlee-test"):
        connections.extend(page['Items'])

    my_connection_id = event['requestContext']['connectionId']

    # Find request user's connection information
    my_info = None
    for connection in connections:
        if connection['connectionID']['S'] == my_connection_id:
            my_info = connection
            break
    if my_info is None:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': "Cannot find your connection information"})
        }
    
    apigatewaymanagementapi = boto3.client(
        'apigatewaymanagementapi',
        endpoint_url=f"https://{event['requestContext']['domainName']}/{event['requestContext']['stage']}"
    )
    
    opinion = json.loads(event['body'])['opinion']
    
    # Broadcast user's opinion to same team.
    for connection in connections:
        other_connection = connection['connectionID']['S']
        if other_connection != my_info['connectionID']['S'] and connection['battleID']['S'] == my_info['battleID']['S'] and connection['teamID']['S'] == my_info['teamID']['S']:
            apigatewaymanagementapi.post_to_connection(
                Data=opinion,
                ConnectionId=other_connection
            )
        
    return {
        'statusCode': 200,
        'body': json.dumps({'message': "Post your opinion to your team"})
    }