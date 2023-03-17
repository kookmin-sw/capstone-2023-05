import json

from src.utility.context import PostgresContext, RedisContext
from src.game.config import redis_config, db_config


def hello(event):
    body = {
        "message": "Hello World!",
        "event": event,
    }
    return {"statusCode": 200, "body": json.dumps(body)}


def hello_redis():
    with RedisContext(**redis_config) as redis:
        return redis.client_info()


def hello_db():
    with PostgresContext(**db_config) as db:
        return f"Database {db.info.host} Connected"
