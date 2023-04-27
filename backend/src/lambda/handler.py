import json
import platform
import random
import csv
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
            select_query = f"SELECT teamid, name FROM team WHERE battleid = \'{battle_id}\'"
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
            'statusCode': 404,
            'body': json.dumps({'message': "Cannot find your connection information"})
        }
    
    # 같은 팀에게 자신의 의견을 broadcasting 한다.
    opinion = json.loads(event['body'])['opinion']
    user_id, battle_id, team_id, nickname = my_info['userID']['S'], my_info['battleID']['S'], my_info['teamID']['S'], my_info['nickname']['S']
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

    # PK: userId, battleId, roundNo, time
    # extra fields: noOfLikes, content, status
    round, num_of_likes = json.loads(event['body'])['round'], 0
    status = "CANDIDATE"

    with PostgresContext(**config.db_config) as psql_ctx:
        with psql_ctx.cursor() as psql_cursor:
            insert_query = f'INSERT INTO Opinion VALUES (\'{user_id}\', \'{battle_id}\', {round}, \'{opinion_time}\', {num_of_likes}, \'{opinion}\', \'{status}\')'
            psql_cursor.execute(insert_query)
            psql_ctx.commit()

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
            select_query = f"SELECT name FROM team WHERE battleid = \'{battle_id}\' and teamid = \'{team_id}\'"
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
    
    # Support 테이블에 팀 선택 기록 저장
    round = json.loads(event['body'])['round']
    with PostgresContext(**config.db_config) as psql_ctx:
        with psql_ctx.cursor() as psql_cursor:
            insert_query = f'INSERT INTO Support VALUES (\'{user_id}\', \'{battle_id}\', {round}, {team_id}, \'{vote_time}\')'
            psql_cursor.execute(insert_query)
            psql_ctx.commit()

    response = {
        'statusCode': 200,
        'body': 'Vote Success'
    }
    return response


@wsclient
def get_new_ads(event, context, wsclient):
    # 라운드 시작 시간을 얻어서 Refresh 주기를 계산
    curr_time = datetime.fromtimestamp(time.time())
    my_battle_id, curr_round = json.loads(event['body'])['battleId'], json.loads(event['body'])['round']
    with PostgresContext(**config.db_config) as psql_ctx:
        with psql_ctx.cursor() as psql_cursor:
            select_query = f'SELECT starttime from Round WHERE battleid = \'{my_battle_id}\' and roundno = {curr_round}'
            psql_cursor.execute(select_query)
            row = psql_cursor.fetchall()
            round_start_time = row[0][0]
    refresh_term = curr_time - round_start_time

    # 요청에 보낸 12개 중 상위 3개 선정
    old_ads = sorted(json.loads(event['body'])['currAds'], key=lambda x: x['likes'], reverse=True)
    new_ads = []
    if len(old_ads) == 12:
        new_ads.extend(old_ads[:3])

    # 의견들을 얻기
    candidates = []
    with PostgresContext(**config.db_config) as psql_ctx:
        with psql_ctx.cursor() as psql_cursor:
            select_query = f'SELECT (userid, nooflikes, content) FROM opinion WHERE battleid = \'{my_battle_id}\' and roundno = {curr_round} and status = \'CANDIDATE\' and time > \'{round_start_time}\''
            psql_cursor.execute(select_query)
            rows = psql_cursor.fetchall()

    # 의견들 중 같은 팀의 의견만을 뽑아내기
    for row in rows:
        f = csv.reader([row[0]], delimiter=',', quotechar='\"')
        row = next(f); row[0] = row[0][1:]; row[2] = row[2][:-1]
        team_id = dynamo_db.scan(
            TableName=config.DYNAMODB_WS_CONNECTION_TABLE,
            FilterExpression="userID = :user_id",
            ExpressionAttributeValues={":user_id": {"S": row[0]}},
            ProjectionExpression="teamID"
        )['Items'][0]['teamID']['S']

        if team_id == json.loads(event['body'])['teamId']:
            candidates.append({
                "userId": row[0],
                "likes": row[1],
                "content": row[2]
            })

    # candidates 중 9개 랜덤 선정
    new_ads.extend(random.sample(candidates, 9 if len(new_ads) > 0 else 12))

    # refresh 이후 likes 수는 모두 0으로 초기화
    for ad in new_ads:
        ad['likes'] = 0

    # New Ads 전송
    wsclient.send(
        connection_id=event['requestContext']['connectionId'],
        data={
            "action": "recvNewAds",
            "result": "success",
            "newAds": new_ads
        }
    )

    response = {
        'stautsCode': 200,
        'body': 'Getting New Ads Success'
    }
    return response
