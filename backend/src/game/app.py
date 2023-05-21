import json
import boto3
import time
import random
import csv
import string
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
    user_id, battle_id, team_id, nickname = my_info['userID']['S'], my_info[
        'battleID']['S'], my_info['teamID']['S'], my_info['nickname']['S']
    status = "CANDIDATE"

    insert_query = f'INSERT INTO \"Opinion\" (\"userId\", \"battleId\", \"roundNo\", \"noOfLikes\", content, \"timestamp\", \"publishTime\", \"dropTime\", \"status\") VALUES (\'{user_id}\', \'{battle_id}\', {round}, {num_of_likes}, \'{opinion}\', NOW() AT TIME ZONE \'UTC\' + INTERVAL \'9 hours\', NULL, NULL, \'{status}\')'
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
    battle_id, user_id, nickname = response[0]['battleID'][
        'S'], response[0]['userID']['S'], response[0]['nickname']['S']
    team_id = json.loads(event['body'])['teamId']

    # DynamoDB에 팀 선택 결과 반영
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


def get_best_opinions(n_best_opinions, candidate_dropped_opinions):
    # 비교 함수
    def helper(opinion):
        status = opinion['status']
        likes = opinion['likes']

        if status == 'CANDIDATE':
            return -1

        publish_time = datetime.strptime(
            opinion['publishTime'], '%Y-%m-%d %H:%M:%S.%f')
        drop_time = datetime.strptime(
            opinion['dropTime'], '%Y-%m-%d %H:%M:%S.%f') if opinion['dropTime'] else None

        time_alive = 0
        # PUBLISHED의 기준
        if status == "PUBLISHED":
            now = datetime.now()
            time_alive = (now - publish_time).total_seconds()

        # DROPPED의 기준:
        elif status == "DROPPED" and drop_time is not None:
            time_alive = (drop_time - publish_time).total_seconds()

        # Criteria for comparing
        compare_value = likes / time_alive
        return compare_value

    best_opinions = candidate_dropped_opinions

    # 팀별로 Sort() & Filter & Limit N
    for team_i in range(len(best_opinions)):
        best_opinions[team_i].sort(key=lambda x: helper(x), reverse=True)
        best_opinions[team_i] = list(
            filter(lambda x: x['status'] != 'CANDIDATE', best_opinions[team_i]))

        # Limit N
        if len(best_opinions[team_i]) > n_best_opinions:
            best_opinions[team_i] = best_opinions[team_i][:n_best_opinions]
    return best_opinions


def preparation_start_handler(event, context, wsclient):
    # 토론의 Host와 라운드의 갱신 주기, 갱신 횟수 얻기
    my_battle_id = json.loads(event['body'])['battleId']
    select_query = f'SELECT (\"refreshPeriod\", \"maxNoOfRefresh\", \"ownerId\") FROM \"DiscussionBattle\" WHERE \"battleId\" = \'{my_battle_id}\''
    rows = psql_ctx.execute_query(select_query)
    f = csv.reader([rows[0][0]], delimiter=',', quotechar='\"')
    single_row = next(f)
    single_row[0] = int(single_row[0][1:])
    single_row[1] = int(single_row[1])
    single_row[2] = single_row[2][:-1]
    refresh_time, refresh_cnt, owner_id = single_row

    # 토론의 팀 ID 값 얻기
    select_query = f"SELECT \"teamId\" FROM \"Team\" WHERE \"battleId\" = \'{my_battle_id}\'"
    team_ids = [row[0] for row in psql_ctx.execute_query(select_query)]

    # 토론에 참여하고 있는 connection들 얻기
    response = dynamo_db.scan(
        TableName=config.DYNAMODB_WS_CONNECTION_TABLE,
        FilterExpression="battleID = :battle_id",
        ExpressionAttributeValues={":battle_id": {"S": my_battle_id}},
        ProjectionExpression="connectionID,userID,teamID"
    )['Items']
    information = [{"connectionID": connection['connectionID']['S'], "userID": connection['userID']
                    ['S'], "teamID": connection['teamID']['S']} for connection in response]

    old_ads = [[], []]
    for cnt in range(refresh_cnt):
        time.sleep(refresh_time)

        # 현재 라운드의 모든 의견을 가져온다.
        my_battle_id, curr_round = json.loads(
            event['body'])['battleId'], json.loads(event['body'])['round']
        select_query = f"""SELECT ("Opinion"."userId","Opinion"."order","Opinion"."noOfLikes","Opinion"."content", "Opinion"."publishTime", "Opinion"."dropTime", "Opinion"."status","Support"."vote") FROM "Opinion", "Support" 
        WHERE "Opinion"."userId" = "Support"."userId" and "Opinion"."battleId" = '{my_battle_id}' and "Support"."battleId" = '{my_battle_id}' and "Opinion"."roundNo" = {curr_round} and "Support"."roundNo" = {curr_round} and status != 'REPORTED'"""
        rows = psql_ctx.execute_query(select_query)

        # 팀별로 의견을 나눈다.
        candidates, all_candidates_dropped = [[], []], [[], []]
        for row in rows:
            f = csv.reader([row[0]], delimiter=',', quotechar='\"')
            row = next(f)
            return_info = {"userId": row[0][1:], "order": int(row[1]), "likes": int(
                row[2]), "content": row[3], "publishTime": row[4], "dropTime": row[5], "status": row[6]}
            if int(row[-1][:-1]) == team_ids[0]:
                all_candidates_dropped[0].append(return_info)
                if return_info["status"] == "CANDIDATE":
                    candidates[0].append(return_info)
            else:
                all_candidates_dropped[1].append(return_info)
                if return_info["status"] == "CANDIDATE":
                    candidates[1].append(return_info)

        sampling_number = 12
        tmp = [[], []]
        publish_orders, drop_orders = [], []
        for idx in range(len(old_ads)):
            # 처음에 요청했다면, Ads는 존재하지 않기 때문
            if len(old_ads[idx]):
                # refresh_cnt 값이 2 이상이면, 기존에 살아남았던 상위 3개의 Ads는 한 번만 더 살아남고 DROPPED 되어야 한다.
                # tmp[idx]의 0번부터 2번 index까지 기존에 살아남았던 상위 3개의 Ads를 담고 있으므로 이들을 잘라낸다.
                if cnt >= 2:
                    drop_orders.extend([str(ad["order"])
                                       for ad in old_ads[idx][:3]])
                    old_ads[idx] = old_ads[idx][3:]

                for ad in old_ads[idx]:
                    ad["likes_per_refresh_time"] = ad["likes"] / refresh_time
                old_ads[idx].sort(
                    key=lambda x: x["likes_per_refresh_time"], reverse=True)
                tmp[idx].extend(old_ads[idx][:3])
                drop_orders.extend([str(ad["order"])
                                   for ad in old_ads[idx][3:]])

            # candidates 중 랜덤 선정
            if (not len(old_ads[idx]) and len(candidates[idx]) <= 12) or (len(old_ads[idx]) and len(candidates[idx]) < 9):
                sampling_number = len(candidates[idx])
            elif len(old_ads[idx]) and len(candidates[idx]) >= 9:
                sampling_number = 9
            tmp[idx].extend(random.sample(candidates[idx], sampling_number))
            for ad in tmp[idx][3:] if refresh_cnt else tmp[idx]:
                publish_orders.append(str(ad['order']))

        if len(publish_orders):
            update_query = f'UPDATE \"Opinion\" SET \"publishTime\"=NOW() AT TIME ZONE \'UTC\' + INTERVAL \'9 hours\' , \"status\" = \'PUBLISHED\' WHERE \"order\" IN ({",".join(publish_orders)})'
            psql_ctx.execute_query(update_query)
        if len(drop_orders):
            update_query = f'UPDATE \"Opinion\" SET \"dropTime\"=NOW() AT TIME ZONE \'UTC\' + INTERVAL \'9 hours\' , \"status\" = \'DROPPED\' WHERE \"order\" IN ({",".join(drop_orders)})'
            psql_ctx.execute_query(update_query)

        # tmp에 있는 불필요 정보 삭제해서 new_ads로 복사
        new_ads = deepcopy(tmp)
        for idx in range(len(new_ads)):
            for new_ad in new_ads[idx]:
                del new_ad['order']
                del new_ad['publishTime']
                del new_ad['dropTime']
                del new_ad['status']
                if 'likes_per_refresh_time' in new_ad:
                    del new_ad['likes_per_refresh_time']

        # 베스트 의견 선정 및 계산
        best_opinions = get_best_opinions(
            n_best_opinions=3, candidate_dropped_opinions=all_candidates_dropped)

        # best_opinions에 있는 불필요 정보 삭제
        for team_id in range(len(new_ads)):
            for opinion in best_opinions[team_id]:
                del opinion['order']
                del opinion['publishTime']
                del opinion['dropTime']
                del opinion['status']

        for info in information:
            # Host는 양 팀의 Ads를 모두 확인할 수 있어야 한다.
            if info['userID'] == owner_id:
                wsclient.send(
                    connection_id=info['connectionID'],
                    data={
                        "action": "recvNewAds",
                        "result": "success",
                        "bestOpinions": best_opinions,
                        "newAds": new_ads,
                    }
                )
            else:    # 참여자는 자신의 팀의 Ads만 받아야 한다.
                wsclient.send(
                    connection_id=info['connectionID'],
                    data={
                        "action": "recvNewAds",
                        "result": "success",
                        "bestOpinions": best_opinions[0] if int(info['teamID']) == team_ids[0] else best_opinions[1],
                        "newAds": new_ads[0] if int(info['teamID']) == team_ids[0] else new_ads[1]
                    }
                )

        old_ads = tmp

    response = {
        'stautsCode': 200,
        'body': 'Getting New Ads Success'
    }
    return response


def response_creator(code, message, data):
    return {
        "statusCode": code,
        "body": json.dumps({
            "message": message,
            "data": data
        })
    }


def id_generator(size=6, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    """
        Generate random string sequence
        Arguments:
            lenght: int
        Returns:
            Random 6 string sequence
    """
    return ''.join(random.choice(chars) for _ in range(size))


def create_battle(event, context, wsclient):
    body = json.loads(event['body'])

    connection_id = event['requestContext']['connectionId']

    battle_title = body['title']

    team_name_a = body['teamNameA']
    team_name_b = body['teamNameB']

    try:
        with PostgresContext(**db_config) as psql_ctx:
            with psql_ctx.cursor() as psql_cursor:
                battle_id = id_generator()

                # Checking Duplicate IDs
                duplicate_check_query = f"""SELECT \"battleId\" from \"DiscussionBattle\";"""
                psql_cursor.execute(duplicate_check_query)
                query_result = psql_cursor.fetchall()
                existing_battle_ids = [result[0] for result in query_result]

                while battle_id in existing_battle_ids:
                    battle_id = id_generator()

                # Create Battle
                psql_cursor.execute(f"""INSERT INTO \"DiscussionBattle\" VALUES (
                    \'{battle_id}\',
                    \'{body['ownerId']}\',
                    \'{body['title']}\',
                    \'BEFORE_OPEN\',
                    null,
                    null,
                    \'{body['description']}\',
                    \'{body['refreshPeriod']}\',
                    \'{body['maxNoOfRefresh']}\',
                    \'{body['maxNoOfRounds']}\',
                    \'{body['maxNoOfVotes']}\',
                    \'{body['maxNoOfOpinion']}\'
                )
                """)

                # Create N Rounds
                for round_no in range(1, body['maxNoOfRounds'] + 1):
                    psql_cursor.execute(
                        f"""
                            INSERT INTO \"Round\" 
                            VALUES (
                                \'{battle_id}\',
                                \'{round_no}\',
                                null,
                                null,
                                \'{'description'}'
                            )
                            RETURNING *;
                        """
                    )

                # Create 2 Teams
                for team_name in (team_name_a, team_name_b):
                    psql_cursor.execute(
                        f"""INSERT INTO \"Team\" 
                        
                        VALUES (
                                DEFAULT,
                                \'{battle_id}\',
                                \'{team_name}\',
                                \'{"www.naver.com"}\'
                            )
                            RETURNING *;
                        """
                    )

                psql_ctx.commit()

        wsclient.send(
            connection_id=connection_id,
            data={
                'message': 'Battle Creation Success',
                'data': {
                    "battle_id": battle_id,
                    "battle_title": battle_title,
                }
            }
        )
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Room creation success",
                "data": {
                    "battle": {
                        "battle_id": battle_id,
                        "battle_title": battle_title,
                    },
                }
            })
        }
    except Exception as e:
        wsclient.send(
            connection_id=connection_id,
            data={
                'message': 'Failed',
                'data': {
                    "e": str(e)
                }
            }
        )
        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": str(e)
            })
        }


def get_battles(event, context, wsclient):
    connection_id = event['requestContext']['connectionId']
    try:
        with PostgresContext(**db_config) as psql_ctx:
            with psql_ctx.cursor() as psql_cursor:
                query = f"select * from \"DiscussionBattle\";"
                psql_cursor.execute(query)
                rows = psql_cursor.fetchall()

        result = json.dumps(rows, default=str)
        wsclient.send(
            connection_id=connection_id,
            data={
                'message': 'Request Success',
                'battles': result
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "Result": result
            })
        }
    except Exception as e:
        wsclient.send(
            connection_id=connection_id,
            data={
                'message': 'Failed',
                'data': {
                    "e": str(e)
                }
            }
        )
        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": json.dumps(e)
            })
        }


def get_battle(event, context, wsclient):
   # Get URL path parameter: battleId
    body = json.loads(event['body'])
    battle_id = body['battleId']
    connection_id = event['requestContext']['connectionId']

    try:
        with PostgresContext(**db_config) as psql_ctx:
            with psql_ctx.cursor() as psql_cursor:
                query = f"""select * from \"DiscussionBattle\" where \"battleId\"=\'{battle_id}\'"""
                psql_cursor.execute(query)
                rows = psql_cursor.fetchall()

        result = json.dumps(rows, default=str)
        wsclient.send(
            connection_id=connection_id,
            data={
                'message': 'Request Success',
                'battles': result
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "Result": result
            })
        }

    except Exception as e:
        wsclient.send(
            connection_id=connection_id,
            data={
                'message': 'Failed',
                'data': {
                    "e": str(e)
                }
            }
        )
        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": str(e)
            })
        }


def start_battle(event, context, wsclient):
    # Get URL path parameter: battleId
    body = json.loads(event['body'])
    battle_id = body['battleId']
    connection_id = event['requestContext']['connectionId']

    try:
        with PostgresContext(**db_config) as psql_ctx:
            with psql_ctx.cursor() as psql_cursor:
                query = f"""UPDATE \"DiscussionBattle\" SET \"status\"='RUNNING', \"startTime\"=NOW() AT TIME ZONE \'UTC\' + INTERVAL \'9 hours\' WHERE \"battleId\"=\'{battle_id}\' RETURNING *;"""
                psql_cursor.execute(query)
                rows = psql_cursor.fetchall()
                psql_ctx.commit()

        result = json.dumps(rows, default=str)

        wsclient.send(
            connection_id=connection_id,
            data={
                'message': 'Request Success',
                'battles': result
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "Result": json.dumps(rows, default=str)
            })
        }
    except Exception as e:
        wsclient.send(
            connection_id=connection_id,
            data={
                'message': 'Failed',
                'data': {
                    "e": str(e)
                }
            }
        )
        print(e)
        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": str(e)
            })
        }


def end_battle(event, context, wsclient):
    connection_id = event['requestContext']['connectionId']
    # Get URL path parameter: battleId
    body = json.loads(event['body'])
    battle_id = body['battleId']

    try:
        with PostgresContext(**db_config) as psql_ctx:
            with psql_ctx.cursor() as psql_cursor:
                query = f"""UPDATE \"DiscussionBattle\" SET \"status\"='CLOSED', \"endTime\"= NOW() AT TIME ZONE \'UTC\' + INTERVAL \'9 hours\' WHERE \"battleId\"=\'{battle_id}\' RETURNING *;"""
                psql_cursor.execute(query)
                rows = psql_cursor.fetchall()
                psql_ctx.commit()
        result = json.dumps(rows, default=str)

        wsclient.send(
            connection_id=connection_id,
            data={
                'message': 'Battle Ended',
                'battle_id': battle_id 
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "Result": str(rows)
            })
        }
    except Exception as e:
        wsclient.send(
            connection_id=connection_id,
            data={
                'message': 'Failed',
                'data': {
                    "e": str(e)
                }
            }
        )

        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": str(e)
            })
        }


def parse_sql_result(rows, keys):
    if not rows:
        return []

    if len(rows[0]) != len(keys):
        return Exception('Keys don\'t match the row results')

    parsed_result = []
    for row in rows:
        parsed_result.append(dict(zip(keys, row)))

    # For Integrity of datetime
    parsed_result = json.loads(json.dumps(parsed_result, default=str))
    return parsed_result


def get_current_round(event, context, wsclient):
    connection_id = event['requestContext']['connectionId']

    data = json.loads(event['body'])
    battle_id = data['battleId']
    try:
        # Get current round from DynamoDB
        with PostgresContext(**db_config) as psql_ctx:
            with psql_ctx.cursor() as psql_cursor:
                round_query = f"""
                        SELECT * FROM \"Round\" WHERE \"battleId\"=\'{battle_id}\'
                        AND \"endTime\" IS NULL 
                        AND \"startTime\" IS NOT NULL
                        ORDER BY \"roundNo\" DESC
                        LIMIT 1;
                        """
                psql_cursor.execute(round_query)

                rows = psql_cursor.fetchall()
                psql_ctx.commit()
        parsed_rows = parse_sql_result(
            rows=rows, keys=["battleId", "roundNo", "startTime", "endTime", "description"])

        # Get DynamoDB connection ID's
        paginator = dynamo_db.get_paginator('scan')
        connections = []
        for page in paginator.paginate(TableName=config.DYNAMODB_WS_CONNECTION_TABLE):
            connections.extend(page['Items'])

        for connection in connections:
            other_connection = connection['connectionID']['S']
            if connection['battleID']['S'] == battle_id:
                wsclient.send(
                    connection_id=other_connection,
                    data={
                        "action": "getCurrentRound",
                        "battleId": battle_id,
                        "currentRound": parsed_rows
                    }
                )
        return {
            "statusCode": 200,
            "body": json.dumps({
                "Result": "Success"
            })
        }
    except Exception as e:
        wsclient.send(
            connection_id=connection_id,
            data={
                "error": str(e)
            }
        )

        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": str(e)
            })
        }

# Helper Function


def get_start_round(battle_id):
    # Get current round from DynamoDB
    with PostgresContext(**db_config) as psql_ctx:
        with psql_ctx.cursor() as psql_cursor:
            round_query = f"""
                    SELECT * FROM \"Round\" WHERE \"battleId\"=\'{battle_id}\'
                    AND \"endTime\" IS NULL 
                    AND \"startTime\" IS NULL
                    ORDER BY \"roundNo\" ASC
                    LIMIT 1;
                    """
            psql_cursor.execute(round_query)

            rows = psql_cursor.fetchall()
            psql_ctx.commit()
    parsed_rows = parse_sql_result(
        rows=rows, keys=["battleId", "roundNo", "startTime", "endTime", "description"])
    if parsed_rows and type(parsed_rows) is list:
        return parsed_rows[0]["roundNo"]
    else:
        return -1 

def get_single_current_round(battle_id):
    # Get current round from DynamoDB
    with PostgresContext(**db_config) as psql_ctx:
        with psql_ctx.cursor() as psql_cursor:
            round_query = f"""
                    SELECT * FROM \"Round\" WHERE \"battleId\"=\'{battle_id}\'
                    AND \"endTime\" IS NULL 
                    AND \"startTime\" IS NOT NULL
                    ORDER BY \"roundNo\" ASC
                    LIMIT 1;
                    """
            psql_cursor.execute(round_query)

            rows = psql_cursor.fetchall()
            psql_ctx.commit()
    parsed_rows = parse_sql_result(
        rows=rows, keys=["battleId", "roundNo", "startTime", "endTime", "description"])
    if parsed_rows and type(parsed_rows) is list:
        return parsed_rows[0]["roundNo"]
    else:
        return -1 

def get_max_rounds_no(battle_id):
    # Get Maximum round count from discussion battle
    with PostgresContext(**db_config) as psql_ctx:
        with psql_ctx.cursor() as psql_cursor:
            round_query = f"""
                    SELECT \"maxNoOfRounds\" from \"DiscussionBattle\" where \"battleId\" = \'{battle_id}\';
                """
            psql_cursor.execute(round_query)
            rows = psql_cursor.fetchall()
            parsed_rows = parse_sql_result(rows, ["maxNoOfRounds"])
    if parsed_rows and type(parsed_rows) is list:
        return parsed_rows[0]['maxNoOfRounds']
    else:
        return -1


def start_round(event, context, wsclient):
    connection_id = event['requestContext']['connectionId']
    body = json.loads(event['body'])
    battle_id = body['battleId']
    current_round = get_start_round(battle_id=battle_id)
    
    try:
        if current_round == -1:
            raise Exception('Either the battle ended or no round was found')
        with PostgresContext(**db_config) as psql_ctx:
            with psql_ctx.cursor() as psql_cursor:
                round_query = f"""
                            UPDATE \"Round\"
                            SET \"startTime\" = NOW() AT TIME ZONE \'UTC\' + INTERVAL \'9 hours\'
                            WHERE \"battleId\" = \'{battle_id}\' AND \"roundNo\" = {current_round}
                            RETURNING *;
                        """
                psql_cursor.execute(round_query)

                rows = psql_cursor.fetchall()
                psql_ctx.commit()
        result = json.dumps(rows, default=str)

        wsclient.send(
            connection_id=connection_id,
            data={
                'message': 'Request Success',
                'Result': result
            }
        )

        # Broadcast current rounds to host, user
        get_current_round(event, context, wsclient)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "Result": result
            })
        }
    except Exception as e:
        wsclient.send(
            connection_id=connection_id,
            data={
                'message': 'Request Failed',
                'Result': str(e)
            }
        )
        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": str(e)
            })
        }


def end_round(event, context, wsclient):
    connection_id = event['requestContext']['connectionId']
    body = json.loads(event['body'])
    battle_id = body['battleId']
    current_round = get_single_current_round(battle_id=battle_id)
    max_no_of_rounds = get_max_rounds_no(battle_id=battle_id)
    print(current_round, max_no_of_rounds)

    try:
        if current_round == -1 or max_no_of_rounds == -1:
            raise Exception('Either the battle ended or no round was found')

        with PostgresContext(**db_config) as psql_ctx:
            with psql_ctx.cursor() as psql_cursor:
                round_query = f"""
                        UPDATE \"Round\"
                        SET \"endTime\" = NOW() AT TIME ZONE \'UTC\' + INTERVAL \'9 hours\' WHERE \"battleId\" = \'{battle_id}\' AND \"roundNo\" = \'{current_round}\'
                        RETURNING *;
                    """
                psql_cursor.execute(round_query)

                rows = psql_cursor.fetchall()
                psql_ctx.commit()
        result = json.dumps(rows, default=str)

       
        wsclient.send(
            connection_id=connection_id,
            data={
                'message': 'Request Success',
                'Result': f"""Round ended: {current_round} / Total Rounds: {max_no_of_rounds}"""
            }
        )

        # Check endbattle
        if current_round == max_no_of_rounds:
            end_battle(event, context, wsclient)


        return {
            "statusCode": 200,
            "body": json.dumps({
                "Result": str(rows)
            })
        }
    except Exception as e:
        wsclient.send(
            connection_id=connection_id,
            data={
                'message': 'Request Failed',
                'Result': str(e)
            }
        )

        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": str(e)
            })
        }


def finish_battle_handler(event, context, wsclient):
    my_battle_id = json.loads(event['body'])['battleId']
    response = dynamo_db.scan(
        TableName=config.DYNAMODB_WS_CONNECTION_TABLE,
        FilterExpression="battleID = :battle_id",
        ExpressionAttributeValues={":battle_id": {"S": my_battle_id}},
        ProjectionExpression="connectionID,userID,teamID"
    )['Items']
    connections = [connection['connectionID']['S'] for connection in response]

    select_query = f"SELECT \"maxNoOfRounds\" FROM \"DiscussionBattle\" WHERE \"battleId\" = \'{my_battle_id}\'"
    row = psql_ctx.execute_query(select_query)
    max_rounds = row[0][0]

    select_query = f"SELECT \"vote\", COUNT(\"vote\") FROM \"Support\" WHERE \"battleId\" = \'{my_battle_id}\' and \"roundNo\" = {max_rounds} GROUP BY \"vote\""
    rows = psql_ctx.execute_query(select_query)
    return_obj = {str(team_id): vote_cnt for team_id, vote_cnt in rows}

    for connection in connections:
        wsclient.send(
            connection_id=connection,
            data={
                "action": "getFinalResult",
                "result": return_obj
            }
        )

    response = {
        'stautsCode': 200,
        'body': 'Getting Final Result Success'
    }
    return response
