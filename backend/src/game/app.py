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

        # Query Parameters
        battle_id =   # 6 characters random

        print(id_generator(size=6))

        # Run Query
        cur.execute(
            f"""INSERT INTO DiscussionBattle(
                    battleId,
                    ownerId, 
                    title,
                    battle_status,
                    visibility,
                    switchChance,
                    startTime,
                    endTime,
                    description,
                    maxNoOfRounds,
                    maxNoVotes,
                    maxNoOfOpinion
                ) VALUES(
                    \'{id_generator()}\', 
                    \'{id_generator()}\',
                    \'{body['title']}\',
                    \'{body['battle_status']}\',
                    \'{body['visibility']}\',
                    \'{body['switchChance']}\',
                    \'{body['startTime']}\',
                    \'{0}\',
                    \'{body['description']}\',
                    \'{body['maxNoOfRounds']}\',
                    \'{body['maxNoOfOpinion']}\',
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
                "Result": "Room creation success"
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
