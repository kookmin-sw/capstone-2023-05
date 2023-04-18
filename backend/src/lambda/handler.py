import json
import platform
import os
import time
from datetime import datetime
import boto3

from src.game import app
from src.game import config

from src.utility.context import PostgresContext
from src.utility.decorator import cors
from src.utility.websocket import wsclient


dynamo_db = boto3.client(**config.dynamo_db_config)


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
    return {
        'statusCode': 200,
        'body': json.dumps({"message": "Connect Success"})
    }


def disconnect_handler(event, context):
    connection_id = event['requestContext']['connectionId']

    # Find request user's battle id
    response = dynamo_db.scan(
        TableName=config.DYNAMODB_WS_CONNECTION_TABLE,
        FilterExpression="connectionID = :connection_id",
        ExpressionAttributeValues={":connection_id": {"S": connection_id}},
        ProjectionExpression="battleID,connectionID"
    )['Items']
    battle_id = response[0]['battleID']['S']
    
    dynamo_db.delete_item(
        TableName=config.DYNAMODB_WS_CONNECTION_TABLE,
        Key={
            'battleID': {'S': battle_id},
            'connectionID': {'S': connection_id}
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': "Delete connection from DB"})
    }


@wsclient
def init_join_handler(event, context, wsclient):
    connection_id = event['requestContext']['connectionId']

    data = json.loads(event['body'])
    battle_id = data['battleId']
    nickname = data['nickname']
    user_id = data['userId']
    team_id = ""

    # DynamoDB에 정보 등록
    dynamo_db.put_item(
        TableName=config.DYNAMODB_WS_CONNECTION_TABLE,
        Item={
            'connectionID': {'S': connection_id},
            'battleID': {'S': battle_id},
            'teamID': {'S': team_id},
            'userID': {'S': user_id},
            'nickname': {'S': nickname}
        }
    )

    # 어떤 팀이 있는지 RDS에서 정보 가져오기
    with PostgresContext(**config.db_config) as psql_ctx:
        with psql_ctx.cursor() as psql_cursor:
            select_query = f"SELECT name FROM team WHERE battleid = \'{battle_id}\'"
            psql_cursor.execute(select_query)
            rows = psql_cursor.fetchall()
            psql_cursor.close()
            team_names = [row for row in rows]
    
    wsclient.send_message(
        connection_id=connection_id,
        message=json.dumps({
            'message': 'Join Request Success',
            'teams': team_names
        })
    )

    response = {
        'statusCode': 200,
        'body': 'Join Request Success'
    }
    return response
    

@wsclient
def send_handler(event, context, wsclient):
    opinion_time = datetime.fromtimestamp(time.time())
    
    # DynamoDB의 모든 값을 얻어온다.
    paginator = dynamo_db.get_paginator('scan')
    connections = []
    for page in paginator.paginate(TableName=config.DYNAMODB_WS_CONNECTION_TABLE):
        connections.extend(page['Items'])

    my_connection_id = event['requestContext']['connectionId']

    # 사용자의 connection 정보를 찾는다.
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
    
    # 같은 팀에게 자신의 의견을 broadcasting 한다.
    opinion = json.loads(event['body'])['opinion']
    user_id, battle_id, team_id, nickname = my_info['userID']['S'], my_info['battleID']['S'], my_info['teamID']['S'], my_info['nickname']['S']
    for connection in connections:
        other_connection = connection['connectionID']['S']
        if connection['battleID']['S'] == battle_id and connection['teamID']['S'] == team_id:
            wsclient.send_message(
                connection_id=other_connection,
                message=f"{nickname}: {opinion}",
            )

    # PK: userId, battleId, roundNo, time
    # extra fields: noOfLikes, content, status
    round, num_of_likes = json.loads(event['body'])['round'], 0
    status = "CANDIDATE"

    with PostgresContext(**config.db_config) as psql_ctx:
        with psql_ctx.cursor() as psql_cursor:
            insert_query = f'INSERT INTO Opinion VALUES (\'{user_id}\', \'{battle_id}\', {round}, {opinion_time}, {num_of_likes}, \'{opinion}\', \'{status}\')'
            psql_cursor.execute(insert_query)
            psql_ctx.client.commit()
            psql_cursor.close()

    response = {
        'statusCode': 200,
        'body': 'Send Success'
    }
    return response