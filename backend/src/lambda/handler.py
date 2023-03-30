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
    
    # battleId, teamId, nickname
    dynamo_db.put_item(
        TableName="websocket-connections-jwlee-test",
        Item={
            'connection-ID': {'S': connection_id},
            'battle-ID': {'S': battle_id},
            'team-ID': {'S': team_id},
            'nickname': {'S': nickname}
        }
    )
    
    return {'statusCode': 200, 'body': json.dumps({'message': "Clear"})}


def disconnect_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    
    dynamo_db.delete_item(
        TableName="websocket-connections-jwlee-test",
        Key={'connection-ID': {'S': connection_id}}
    )
    
    return {'statusCode': 200, 'body': json.dumps({'message': "Clear"})}


def send_handler(event, context):
    paginator = dynamo_db.get_paginator('scan')
    connection_ids = []
    for page in paginator.paginate(TableName="websocket-connections-jwlee-test"):
        connection_ids.extend(page['Items'])

    my_connection = event['requestContext']['connectionId']
    my_info = dynamo_db.get_item(
        TableName="websocket-connections-jwlee-test",
        Key={"connection-ID": {"S": my_connection}}
    )['Item']
    
    apigatewaymanagementapi = boto3.client(
        'apigatewaymanagementapi',
        endpoint_url=f"https://{event['requestContext']['domainName']}/{event['requestContext']['stage']}"
    )
    
    opinion = json.loads(event['body'])['opinion']
        
    for connection in connection_ids:
        other_connection = connection['connection-ID']['S']
        if other_connection != my_info['connection-ID']['S'] and connection['battle-ID']['S'] == my_info['battle-ID']['S'] and connection['team-ID']['S'] == my_info['team-ID']['S']:
            apigatewaymanagementapi.post_to_connection(
                Data=opinion,
                ConnectionId=other_connection
            )
        
    return {'statusCode': 200, 'body': json.dumps({'message': "Clear"})}