import json
import platform
import os
import time
import boto3

from src.game import app
from src.utility.context import PostgresContext


dynamo_db = boto3.client('dynamodb')


def hello(event, context):
    msg = app.hello()
    response = {
        "statusCode": 200,
        "body": msg
    }
    return response


def get_platform(event, context):
    msg = platform.platform()
    response = {
        "statusCode": 200,
        "body": msg
    }
    return response


def hello_redis(event, context):
    client_info = app.hello_redis()
    response = {
        "statusCode": 200,
        "body": json.dumps(client_info)
    }
    return response


def hello_db(event, context):
    msg = app.hello_db()
    response = {
        "statusCode": 200,
        "body": msg
    }
    return response


def connect_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    
    headers = event['headers']
    battle_id = headers['battleId']
    team_id = headers['teamId']
    nickname = headers['nickname']
    email = headers['email']
    
    dynamo_db.put_item(
        TableName="websocket-connections-jwlee-test",
        Item={
            'connectionID': {'S': connection_id},
            'battleID': {'S': battle_id},
            'teamID': {'S': team_id},
            'nickname': {'S': nickname},
            'email': {'S': email}
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
    opinion_time = time.time()
    
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
    
    opinion = my_info['nickname']['S'] + ": " + json.loads(event['body'])['opinion']
    
    # Broadcast user's opinion to same team.
    for connection in connections:
        other_connection = connection['connectionID']['S']
        if connection['battleID']['S'] == my_info['battleID']['S'] and connection['teamID']['S'] == my_info['teamID']['S']:
            apigatewaymanagementapi.post_to_connection(
                Data=opinion,
                ConnectionId=other_connection
            )

    # PK: userId, battleId, roundNo, time
    # extra fields: noOfLikes, content, status
    round, num_of_likes = json.loads(event['body'])['round'], 0
    status = "common"

    psql_ctx = PostgresContext("172.18.0.3", os.getenv("POSTGRESQL_PORT"), os.getenv("POSTGRESQL_USER"),
                               os.getenv("POSTGRESQL_PASSWORD"), os.getenv("POSTGRESQL_DB"))
    psql_cursor = psql_ctx.cursor
    # Or getting email from Postgres Database?
    insert_query = f"INSERT INTO Opinion VALUES (\'{my_info['email']['S']}\', \'{my_info['battleID']['S']}\', {round}, {opinion_time}, {num_of_likes}, \'{opinion}\', \'{status}\')"
    psql_cursor.execute(insert_query)
    psql_ctx.client.commit()

    return {
        'statusCode': 200,
        'body': json.dumps({'message': "Post your opinion to your team"})
    }