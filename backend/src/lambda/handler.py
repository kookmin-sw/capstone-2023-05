import json
import platform
import random
import time
from datetime import datetime
from copy import deepcopy
import boto3

from src.game import app
from src.game import config

from src.utility.context import PostgresContext
from src.utility.decorator import cors
from src.utility.websocket import wsclient


dynamo_db = boto3.client(**config.dynamo_db_config)
psql_ctx = PostgresContext(**config.db_config)


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
            'statusCode': 404,
            'body': json.dumps({'message': "Cannot find your connection information"})
        }
    
    # PK: userId, battleId, roundNo, time
    # extra fields: noOfLikes, content, status
    round, num_of_likes = json.loads(event['body'])['round'], 0
    opinion = json.loads(event['body'])['opinion']
    user_id, battle_id, team_id, nickname = my_info['userID']['S'], my_info['battleID']['S'], my_info['teamID']['S'], my_info['nickname']['S']
    status = "CANDIDATE"

    with PostgresContext(**config.db_config) as psql_ctx:
        with psql_ctx.cursor() as psql_cursor:
            insert_query = f'INSERT INTO \"Opinion\" (\"userId\", \"battleId\", \"roundNo\", \"noOfLikes\", content, \"time\", status) VALUES (\'{user_id}\', \'{battle_id}\', {round}, {num_of_likes}, \'{opinion}\', \'{opinion_time}\', \'{status}\')'
            psql_cursor.execute(insert_query)
            psql_ctx.commit()
    
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
    
    # Support 테이블에 팀 선택 기록 저장
    round = json.loads(event['body'])['round']
    with PostgresContext(**config.db_config) as psql_ctx:
        with psql_ctx.cursor() as psql_cursor:
            insert_query = f'INSERT INTO \"Support\" VALUES (\'{user_id}\', \'{battle_id}\', {round}, {team_id}, \'{vote_time}\')'
            psql_cursor.execute(insert_query)
            psql_ctx.commit()

    response = {
        'statusCode': 200,
        'body': 'Vote Success'
    }
    return response


@wsclient
def get_new_ads(event, context, wsclient):
    # 1. 갱신 단위 시간, 갱신 횟수를 "DiscussionBattle" 테이블에서 찾는다
    my_battle_id = json.loads(event['body'])['battleId']
    select_query = f'SELECT (\"refreshPeriod\", \"maxNoOfRefresh\") FROM \"DiscussionBattle\" WHERE \"battleId\" = \'{my_battle_id}\''
    rows = psql_ctx.execute_query(select_query)
    single_row = eval(rows[0][0])
    refresh_time, refresh_cnt = single_row[0], single_row[1]
    
    # 갱신 횟수 만큼 반복문 실행, 한 번의 반복이 끝날 때마다 갱신 단위 시간만큼 sleep
    old_ads = []
    for cnt in range(refresh_cnt):
        if cnt < 2:
            time.sleep(refresh_time)

        # 2. "Opinion" 테이블에서 아래의 조건에 모두 부합하는 의견을 얻는다
        my_battle_id, my_team_id, curr_round = json.loads(event['body'])['battleId'], json.loads(event['body'])['teamId'], json.loads(event['body'])['round']
        select_query = f'SELECT * FROM \"Opinion\" WHERE \"battleId\" = \'{my_battle_id}\' and \"roundNo\" = {curr_round} and status != \'REPORTED\''
        rows = psql_ctx.execute_query(select_query)

        # 3. 'PUBLISHED', 'DROPPED' 의견(best3_candidates)은 승호 형의 best3 반환하는 함수로 넘겨준다.
        #    'CANDIDATE' 의견은 내가 사용한다
        #    같은 팀의 의견을 찾기 위해 DynamoDB를 같이 사용한다. 아니면 Support와 Opinion을 JOIN 해서 찾는다?(일단 보류)
        best3_candidates, candidates = [], []
        response = dynamo_db.scan(
            TableName=config.DYNAMODB_WS_CONNECTION_TABLE,
            FilterExpression="battleID = :battle_id",
            ExpressionAttributeValues={":battle_id": {"S": my_battle_id}},
            ProjectionExpression="teamID"
        )['Items']

        for row in rows:
            for info in response:
                if info['teamID']['S'] == my_team_id and row[-1] != "CANDIDATE":
                    best3_candidates.append(row[:5])
                elif info['teamID']['S'] == my_team_id and row[-1] == "CANDIDATE":
                    candidates.append({"userId": row[0], "order": row[3], "likes": row[4], "content": row[5]})

        # 4. CANDIDATE 의견들 중에서 랜덤하게 9개(12개)를 선택한다.
        # 그 전에 요청 받은 12개 의견들 중 상위 3개 선정
        tmp = []
        if len(old_ads):    # 처음에 요청했다면, Ads는 존재하지 않기 때문
            for ad in old_ads:
                ad["likes_per_refresh_time"] = ad["likes"] / refresh_time
            old_ads = sorted(old_ads, key=lambda x: x["likes_per_refresh_time"], reverse=True)
            tmp.extend(old_ads[:3])
        
            # 기존의 PUBLISHED 의견 중 상위 3개에 들지 못한 의견들은 DROPPED로 status 변경
            orders = [str(ad['order']) for ad in old_ads[3:]]
            update_query = f'UPDATE \"Opinion\" SET status = \'DROPPED\' WHERE \"order\" IN ({",".join(orders)})'
            psql_ctx.execute_query(update_query)

        # candidates 중 9개 랜덤 선정
        # 만약 처음 요청하는 거면 12개의 새로운 Ads를 줘야 하므로 12개 랜덤 선정
        # 남은 후보가 12개 혹은 9개보다 작으면 모든 후보를 새로운 ads로 선정
        sampling_number = 12
        if len(old_ads) and len(candidates) >= 9:
            sampling_number = 9
        elif len(candidates) < 9:
            sampling_number = len(candidates)
        tmp.extend(random.sample(candidates, sampling_number))

        # status를 CANDIDATE에서 PUBLISHED로 변경
        orders = [str(ad['order']) for ad in tmp]
        update_query = f'UPDATE \"Opinion\" SET status = \'PUBLISHED\' WHERE \"order\" IN ({",".join(orders)})'
        psql_ctx.execute_query(update_query)

        # 5. New Ads 전송
        new_ads = []
        for ad in tmp:
            new_ad = deepcopy(ad)
            del new_ad['order']
            if 'likes_per_refresh_time' in new_ad:
                del new_ad['likes_per_refresh_time']
            new_ads.append(new_ad)

        wsclient.send(
            connection_id=event['requestContext']['connectionId'],
            data={
                "action": "recvNewAds",
                "result": "success",
                "newAds": new_ads
            }
        )

        old_ads = tmp

    response = {
        'stautsCode': 200,
        'body': 'Getting New Ads Success'
    }
    return response
