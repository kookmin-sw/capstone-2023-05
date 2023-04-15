import json

from src.utility.context import PostgresContext, RedisContext
from src.game.config import redis_config, db_config

import json
import psycopg2
import os
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


def create_battle(event, context):
    ENDPOINT = os.environ['POSTGRES_HOST']
    PORT = os.environ['POSTGRES_PORT']
    USER = os.environ['POSTGRES_USER']
    DBNAME = os.environ['POSTGRES_DB']
    PASSWORD = os.environ['POSTGRES_PASSWORD']

    body = json.loads(event['body'])

    battle_title = body['title']

    team_name_a = body['teamNameA']
    team_name_b = body['teamNameB']

    try:
        # Connect to RDS
        conn = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME,
                                user=USER, password=PASSWORD, sslrootcert="SSLCERTIFICATE")
        cur = conn.cursor()

        # Generate Random 6-length string
        battle_id = id_generator()

        # Checks for battle_id duplicate
        cur.execute("SELECT battleid from discussionbattle")
        query_result = cur.fetchall()

        battle_id_list = [result[0] for result in query_result]
        while battle_id in battle_id_list:
            battle_id = id_generator()

        # Create Room
        cur.execute(
            f"""INSERT INTO DiscussionBattle(
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
                    \'{1}\',
                    \'{body['title']}\',
                    \'BEFORE_OPEN\',
                    \'{body['visibility']}\',
                    \'{body['switchChance']}\',
                    null,
                    null,
                    \'{body['description']}\',
                    \'{body['maxNoOfRounds']}\',
                    \'{body['maxNoOfVotes']}\',
                    \'{body['maxNoOfOpinion']}\'
                )
            """
        )

        # Create 2 Teams
        for team_name in (team_name_a, team_name_b):
            cur.execute(
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

        # Create N Rounds
        for round_no in range(1, body['maxNoOfRounds'] + 1):
            cur.execute(
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

        # Apply the change & Close the Connection
        conn.commit()
        cur.close()
        conn.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Room creation success",
                "data": {
                    "battle": {
                        "battle_id": battle_id,
                        "battle_title": battle_title,
                    },
                    "teams": [{"teamNameA": team_name_a,
                               "teamIdA": "",
                               "teamImageA": "www.naver.com"
                               },
                              {
                        "teamNameB": team_name_b,
                        "teamIdB": "",
                        "teamImageB": "www.naver.com"
                    }],
                    "rounds": []
                }
            })
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": str(e)
            })
        }


def get_battles(event, context):
    ENDPOINT = os.environ['POSTGRES_HOST']
    PORT = os.environ['POSTGRES_PORT']
    USER = os.environ['POSTGRES_USER']
    DBNAME = os.environ['POSTGRES_DB']
    PASSWORD = os.environ['POSTGRES_PASSWORD']

    try:
        conn = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME,
                                user=USER, password=PASSWORD, sslrootcert="SSLCERTIFICATE")
        cur = conn.cursor()

        cur.execute("""select * from DiscussionBattle;""")
        query_results = cur.fetchall()

        cur.close()
        conn.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "Result": str(query_results)
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
    ENDPOINT = os.environ['POSTGRES_HOST']
    PORT = os.environ['POSTGRES_PORT']
    USER = os.environ['POSTGRES_USER']
    DBNAME = os.environ['POSTGRES_DB']
    PASSWORD = os.environ['POSTGRES_PASSWORD']

    # Get URL path parameter: battleId
    battle_id = event["pathParameters"]["battleId"]

    try:
        conn = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME,
                                user=USER, password=PASSWORD, sslrootcert="SSLCERTIFICATE")
        cur = conn.cursor()

        cur.execute(
            f"""select * from DiscussionBattle where battleid=\'{battle_id}\';""")
        query_results = cur.fetchall()

        cur.close()
        conn.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "Result": str(query_results)
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


def start_battle(event, context):
    ENDPOINT = os.environ['POSTGRES_HOST']
    PORT = os.environ['POSTGRES_PORT']
    USER = os.environ['POSTGRES_USER']
    DBNAME = os.environ['POSTGRES_DB']
    PASSWORD = os.environ['POSTGRES_PASSWORD']

    # Get URL path parameter: battleId
    battle_id = event["pathParameters"]["battleId"]

    try:
        conn = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME,
                                user=USER, password=PASSWORD, sslrootcert="SSLCERTIFICATE")
        cur = conn.cursor()

        # Update Battle status and start time info
        cur.execute(
            f"""UPDATE discussionbattle SET status=\'RUNNING\', startTime=NOW() WHERE battleid=\'{battle_id}\';""")

        query_results = cur.fetchall()

        cur.close()
        conn.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "Result": str(query_results)
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
    pass


def start_round(event, context):
    pass


def end_round(event, context):
    pass
