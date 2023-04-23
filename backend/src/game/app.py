import json

from src.utility.context import PostgresContext, RedisContext
from src.game.config import redis_config, db_config
import random
import string


def hello():
    return "Hello World!"


def hello_redis():
    with RedisContext(**redis_config) as redis:
        return redis.client_info()


def hello_db():
    with PostgresContext(**db_config) as db:
        return f"Database {db.info.host} Connected"


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
                duplicate_check_query = f"""SELECT battleid from discussionbattle"""
                psql_cursor.execute(duplicate_check_query)
                query_result = psql_cursor.fetchall()
                existing_battle_ids = [result[0] for result in query_result]

                while battle_id in existing_battle_ids:
                    battle_id = id_generator()

                # Create Battle
                psql_cursor.execute(f"""INSERT INTO DiscussionBattle(
                    battleId,
                    ownerId,
                    title,
                    status,
                    visibility,
                    switchChance,
                    startTime,
                    endTime,
                    description,
                    maxNoOfRounds,
                    maxNoOfVotes,
                    maxNoOfOpinion
                ) VALUES (
                    \'{battle_id}\',
                    \'{body['ownerId']}\',
                    \'{body['title']}\',
                    \'BEFORE_OPEN\',
                    \'{body['visibility']}\',
                    \'{body['switchChance']}\',
                    null,
                    null,
                    \'{body['description']}\',
                    0,
                    \'{body['maxNoOfVotes']}\',
                    \'{body['maxNoOfOpinion']}\'
                )
                """)

                # Create N Rounds
                for round_no in range(1, body['maxNoOfRounds'] + 1):
                    psql_cursor.execute(
                        f"""
                            INSERT INTO ROUND(
                                battleId,
                                roundNo,
                                startTime,
                                endTime,
                                description
                            ) VALUES (
                                \'{battle_id}\',
                                \'{round_no}\',
                                null,
                                null,
                                \'{'description'}'
                            )
                        """
                    )

                # Create 2 Teams
                for team_name in (team_name_a, team_name_b):
                    psql_cursor.execute(
                        f"""INSERT INTO Team(
                                teamId,
                                battleId,
                                name,
                                image
                            ) VALUES (
                                DEFAULT,
                                \'{battle_id}\',
                                \'{team_name}\',
                                \'{"www.naver.com"}\'
                            )
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
    try:
        connection_id = event['requestContext']['connectionId']
        with PostgresContext(**db_config) as psql_ctx:
            with psql_ctx.cursor() as psql_cursor:
                query = f"select * from DiscussionBattle;"
                psql_cursor.execute(query)
                rows = psql_cursor.fetchall()

        wsclient.send(
            connection_id=connection_id,
            data={
                'message': 'Request Success',
                'battles': rows
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "Result": rows
            })
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": str(e)
            })
        }


def get_battle(event, context):
   # Get URL path parameter: battleId
    battle_id = event["pathParameters"]["battleId"]

    try:
        with PostgresContext(**db_config) as psql_ctx:
            with psql_ctx.cursor() as psql_cursor:
                query = f"""select * from DiscussionBattle where battleid=\'{battle_id}\'"""
                psql_cursor.execute(query)
                rows = psql_cursor.fetchall()

        return {
            "statusCode": 200,
            "body": json.dumps(rows, indent=4, default=str)

        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": str(e)
            })
        }


def start_battle(event, context):
    # Get URL path parameter: battleId
    battle_id = event["pathParameters"]["battleId"]

    try:
        with PostgresContext(**db_config) as psql_ctx:
            with psql_ctx.cursor() as psql_cursor:
                query = f"""UPDATE discussionbattle SET status='RUNNING', startTime=NOW() WHERE battleid=\'{battle_id}\' RETURNING *;"""
                psql_cursor.execute(query)
                rows = psql_cursor.fetchall()
                psql_ctx.commit()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "Result": json.dumps(rows, default=str)
            })
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": str(e)
            })
        }


def end_battle(event, context):
    # Get URL path parameter: battleId
    battle_id = event["pathParameters"]["battleId"]

    try:
        with PostgresContext(**db_config) as psql_ctx:
            with psql_ctx.cursor() as psql_cursor:
                query = f"""UPDATE discussionbattle SET status='CLOSED', endTime=NOW() WHERE battleid=\'{battle_id}\' RETURNING *;"""
                psql_cursor.execute(query)
                rows = psql_cursor.fetchall()
                psql_ctx.commit()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "Result": str(rows)
            })
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": str(e)
            })
        }


def start_round(event, context):
    # Get URL path parameter: battleId
    battle_id = event["pathParameters"]["battleId"]
    try:
        with PostgresContext(**db_config) as psql_ctx:
            with psql_ctx.cursor() as psql_cursor:
                round_query = f"""
                            UPDATE Round
                            SET startTime = NOW()
                            WHERE battleId = \'{battle_id}\' AND roundNO = (SELECT currentRound+1 FROM DiscussionBattle WHERE battleId = \'{battle_id}\')
                            RETURNING *;
                        """
                battle_query = f"""
                            Update DiscussionBattle
                            SET currentRound = currentRound + 1
                            WHERE battleId =\'{battle_id}\'
                            RETURNING *;
                """
                psql_cursor.execute(round_query)
                psql_cursor.execute(battle_query)

                rows = psql_cursor.fetchall()
                psql_ctx.commit()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "Result": str(rows)
            })
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": str(e)
            })
        }


def end_round(event, context):
    # Get URL path parameter: battleId
    battle_id = event["pathParameters"]["battleId"]
    try:
        with PostgresContext(**db_config) as psql_ctx:
            with psql_ctx.cursor() as psql_cursor:
                round_query = f"""
                        UPDATE Round
                        SET endTime = NOW()
                        WHERE battleId = \'{battle_id}\' AND roundNO = (SELECT currentRound FROM DiscussionBattle WHERE battleId = \'{battle_id}\')
                        RETURNING *;
                    """
                psql_cursor.execute(round_query)

                rows = psql_cursor.fetchall()
                psql_ctx.commit()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "Result": str(rows)
            })
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": str(e)
            })
        }
