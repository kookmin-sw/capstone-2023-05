import json
import platform
import time
from datetime import datetime
from psycopg2.errors import ForeignKeyViolation as fk_violation
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
            select_query = f"SELECT \"teamId\", name FROM \"Team\" WHERE \"battleId\" = \'{battle_id}\'"
            psql_cursor.execute(select_query)
            rows = psql_cursor.fetchall()
            team_names = [{"teamId": row[0], "teamName": row[1]} for row in rows]
    
    wsclient.send(
        connection_id=connection_id,
        data={
            'action': 'initJoinResult',
            'result': 'success',
            'teams': team_names
        }
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
            'statusCode': 400,
            'body': json.dumps({'message': "Cannot find your connection information"})
        }

    # PK: userId, battleId, roundNo, time
    # extra fields: noOfLikes, content, status
    round, num_of_likes = json.loads(event['body'])['round'], 0
    opinion = json.loads(event['body'])['opinion']
    status = "CANDIDATE"
    user_id, battle_id, team_id, nickname = my_info['userID']['S'], my_info['battleID']['S'], my_info['teamID']['S'], my_info['nickname']['S']
    try:
        with PostgresContext(**config.db_config) as psql_ctx:
            with psql_ctx.cursor() as psql_cursor:
                insert_query = f'INSERT INTO \"Opinion\" (\"userId\", \"battleId\", \"roundNo\", \"noOfLikes\", \"content\", \"time\", status) VALUES (\'{user_id}\', \'{battle_id}\', {round}, {num_of_likes}, \'{opinion}\', \'{opinion_time}\', \'{status}\')'
                psql_cursor.execute(insert_query)
                psql_ctx.commit()
    except fk_violation:
        wsclient.send(
                connection_id=my_connection_id,
                data={
                    "action": "recvOpinion",
                    "nickname": "MASTER",
                    "opinion": "You send malformed data."
                }
            )
        return {
            'statusCode': 400,
            'body': 'You tried insert malformed data into DB'
        }

    # 같은 팀에게 자신의 의견을 broadcasting 한다.
    for connection in connections:
        other_connection = connection['connectionID']['S']
        if connection['battleID']['S'] == battle_id and connection['teamID']['S'] == team_id:
            wsclient.send(
                connection_id=other_connection,
                data={
                    "action": "recvOpinion",
                    "nickname": nickname,
                    "opinion": opinion
                }
            )

    response = {
        'statusCode': 200,
        'body': 'Send Success'
    }
    return response


@wsclient
def vote_handler(event, context, wsclient):
    vote_time = datetime.fromtimestamp(time.time())
    connection_id = event['requestContext']['connectionId']

    # DynamoDB에서 유저 정보 찾기
    response = dynamo_db.scan(
        TableName=config.DYNAMODB_WS_CONNECTION_TABLE,
        FilterExpression="connectionID = :connection_id",
        ExpressionAttributeValues={":connection_id": {"S": connection_id}},
        ProjectionExpression="battleID,connectionID,nickname,userID"
    )['Items']
    battle_id, user_id, nickname = response[0]['battleID']['S'], response[0]['userID']['S'], response[0]['nickname']['S']
    team_id = json.loads(event['body'])['teamId']

    # Support 테이블에 팀 선택 기록 저장
    try:
        round = json.loads(event['body'])['round']
        with PostgresContext(**config.db_config) as psql_ctx:
            with psql_ctx.cursor() as psql_cursor:
                insert_query = f'INSERT INTO \"Support\" VALUES (\'{user_id}\', \'{battle_id}\', {round}, {team_id}, \'{vote_time}\')'
                psql_cursor.execute(insert_query)
                psql_ctx.commit()
    except fk_violation:
        wsclient.send(
                connection_id=connection_id,
                data={
                    "action": "voteResult",
                    "result": "fail",
                    "teamId": "None",
                    "teamName": "You send malformed data."
                }
            )
        
    # DynamoDB에 팀 선택 결과 반영
    dynamo_db.put_item(
        TableName=config.DYNAMODB_WS_CONNECTION_TABLE,
        Item={
            'connectionID': {'S': connection_id},
            'battleID': {'S': battle_id},
            'teamID': {'S': str(team_id)},
            'userID': {'S': user_id},
            'nickname': {'S': nickname}
        }
    )

    # 팀 이름을 찾기 위한 SQL문 실행
    with PostgresContext(**config.db_config) as psql_ctx:
        with psql_ctx.cursor() as psql_cursor:
            select_query = f"SELECT name FROM \"Team\" WHERE \"battleId\" = \'{battle_id}\' and \"teamId\" = \'{team_id}\'"
            psql_cursor.execute(select_query)
            row = psql_cursor.fetchall()
            team_name = row[0][0]

    # 팀 선택 결과 전송
    wsclient.send(
        connection_id=connection_id,
        data={
            "action": "voteResult",
            "result": "success",
            "teamId": team_id,
            "teamName": team_name
        }
    )

    response = {
        'statusCode': 200,
        'body': 'Vote Success'
    }
    return response
