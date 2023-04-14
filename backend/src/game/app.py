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


def id_generator(size=6, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    """
        Generate random lowercase string sequence 
        Arguments:
            lenght: int
        Returns:
            Random 6 lowercase string sequence
    """
    return ''.join(random.choice(chars) for _ in range(size))


def create_room(event, context):
    ENDPOINT = os.environ['POSTGRES_HOST']
    PORT = os.environ['POSTGRES_PORT']
    USER = os.environ['POSTGRES_USER']
    DBNAME = os.environ['POSTGRES_DB']
    PASSWORD = os.environ['POSTGRES_PASSWORD']

    try:
        conn = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME,
                                user=USER, password=PASSWORD, sslrootcert="SSLCERTIFICATE")
        cur = conn.cursor()

        body = json.loads(event['body'])
        
        room_id = id_generator()

        # Run Query
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
                    maxNoVotes,
                    maxNoOfOpinion
                ) VALUES (
                    \'{room_id}\', 
                    \'{1}\',
                    \'{body['title']}\',
                    \'{body['battle_status']}\',
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
        conn.commit()

        # Close the Connection
        cur.close()
        conn.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Room creation success",
                "data": {
                    "roomId": room_id
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


def get_room(event, context):
    ENDPOINT = os.environ['POSTGRES_HOST']
    PORT = os.environ['POSTGRES_PORT']
    USER = os.environ['POSTGRES_USER']
    DBNAME = os.environ['POSTGRES_DB']
    PASSWORD = os.environ['POSTGRES_PASSWORD']

    try:
        conn = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME,
                                user=USER, password=PASSWORD, sslrootcert="SSLCERTIFICATE")
        cur = conn.cursor()

        cur.execute("""select * from DiscussionBattle""")
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

def create_team(event, context):
    pass

def get_team(event, context):
    pass

def create_round(event, context):
    pass

def get_round(event, context):
    pass