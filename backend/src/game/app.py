import json
import boto3
import time
import random
import csv
from datetime import datetime
from copy import deepcopy

from src.game import config
from src.game.config import redis_config, db_config, dynamo_db_config

from src.utility.context import PostgresContext, RedisContext
from src.utility.websocket import wsclient

dynamo_db = boto3.client(**dynamo_db_config)
psql_ctx = PostgresContext(**db_config)


def hello():
    return "Hello World!"


def hello_redis():
    with RedisContext(**redis_config) as redis:
        return redis.client_info()


def hello_db():
    with PostgresContext(**db_config) as db:
        return f"Database {db.info.host} Connected"


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
    select_query = f"SELECT \"teamId\", name FROM \"Team\" WHERE \"battleId\" = \'{battle_id}\'"
    rows = psql_ctx.execute_query(select_query)
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

    insert_query = f'INSERT INTO \"Opinion\" (\"userId\", \"battleId\", \"roundNo\", \"noOfLikes\", content, \"time\", status) VALUES (\'{user_id}\', \'{battle_id}\', {round}, {num_of_likes}, \'{opinion}\', \'{opinion_time}\', \'{status}\')'
    psql_ctx.execute_query(insert_query)
    
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
    select_query = f"SELECT name FROM \"Team\" WHERE \"battleId\" = \'{battle_id}\' and \"teamId\" = \'{team_id}\'"
    rows = psql_ctx.execute_query(select_query)
    team_name = rows[0][0]

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
    insert_query = f'INSERT INTO \"Support\" VALUES (\'{user_id}\', \'{battle_id}\', {round}, {team_id}, \'{vote_time}\')'
    psql_ctx.execute_query(insert_query)

    response = {
        'statusCode': 200,
        'body': 'Vote Success'
    }
    return response


def get_new_ads(event, context, wsclient):
    my_battle_id = json.loads(event['body'])['battleId']
    select_query = f'SELECT (\"refreshPeriod\", \"maxNoOfRefresh\") FROM \"DiscussionBattle\" WHERE \"battleId\" = \'{my_battle_id}\''
    rows = psql_ctx.execute_query(select_query)
    single_row = eval(rows[0][0])
    refresh_time, refresh_cnt = single_row[0], single_row[1]
    
    old_ads = []
    for _ in range(refresh_cnt):
        time.sleep(refresh_time)

        my_battle_id, my_team_id, curr_round = json.loads(event['body'])['battleId'], json.loads(event['body'])['teamId'], json.loads(event['body'])['round']
        select_query = f"""SELECT (\"Opinion\".\"userId\",\"Opinion\".\"battleId\",\"Opinion\".\"roundNo\",\"Opinion\".\"order\",\"Opinion\".\"noOfLikes\",\"Opinion\".\"content\",\"Opinion\".status,\"Support\".vote) FROM \"Opinion\", \"Support\" 
        WHERE \"Opinion\".\"userId\" = \"Support\".\"userId\" and \"Opinion\".\"battleId\" = \'{my_battle_id}\' and \"Support\".\"battleId" = \'{my_battle_id}\' and "Opinion"."roundNo" = {curr_round} and "Support"."roundNo" = {curr_round} and status != \'REPORTED\'"""
        rows = psql_ctx.execute_query(select_query)

        # 같은 팀의 의견을 찾기 위해 Support와 Opinion을 JOIN 해서 찾는다.
        best3_candidates, candidates = [], []
        for row in rows:
            f = csv.reader([row[0]], delimiter=',', quotechar='\"')
            row = next(f); row[0] = row[0][1:]; row[2] = int(row[2]); row[3] = int(row[3]); row[4] = int(row[4]); row[-1] = row[-1][:-1]
            if row[-1] == my_team_id and row[-2] != "CANDIDATE":
                best3_candidates.append(row[:5])
            elif row[-1] == my_team_id and row[-2] == "CANDIDATE":
                candidates.append({"userId": row[0], "order": row[3], "likes": row[4], "content": row[5]})

        # 요청 받은 12개 의견들 중 상위 3개 선정
        tmp = []
        if len(old_ads):    # 처음에 요청했다면, Ads는 존재하지 않기 때문
            for ad in old_ads:
                ad["likes_per_refresh_time"] = ad["likes"] / refresh_time
            old_ads = sorted(old_ads, key=lambda x: x["likes_per_refresh_time"], reverse=True)
            tmp.extend(old_ads[:3])
        
            orders = [str(ad['order']) for ad in old_ads[3:]]
            update_query = f'UPDATE \"Opinion\" SET status = \'DROPPED\' WHERE \"order\" IN ({",".join(orders)})'
            psql_ctx.execute_query(update_query)

        # candidates 중 9개 랜덤 선정
        sampling_number = 12
        if len(old_ads) and len(candidates) >= 9:
            sampling_number = 9
        elif len(candidates) < 9:
            sampling_number = len(candidates)
        tmp.extend(random.sample(candidates, sampling_number))

        orders = [str(ad['order']) for ad in tmp]
        update_query = f'UPDATE \"Opinion\" SET status = \'PUBLISHED\' WHERE \"order\" IN ({",".join(orders)})'
        psql_ctx.execute_query(update_query)

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
