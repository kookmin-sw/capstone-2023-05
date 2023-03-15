import json
import tqdm

from src.utility.redis import RedisHelper


def hello(event):
    tqdm.tqdm()
    body = {
        "message": "Hello World!",
        "event": event,
    }
    return {"statusCode": 200, "body": json.dumps(body)}


def create_room(data):
    with RedisHelper() as redis:
        redis.set("test", "test")
