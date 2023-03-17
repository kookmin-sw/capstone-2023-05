import json
import tqdm

from src.utility.context import RedisContext
from src.game.config import redis_config


def hello(event):
    tqdm.tqdm()
    body = {
        "message": "Hello World!",
        "event": event,
    }
    return {"statusCode": 200, "body": json.dumps(body)}


def create_room(data):
    with RedisContext(**redis_config) as redis:
        redis.set("test", "test")
        assert redis.get("test") == "test"
        redis.delete("test")
        assert redis.get("test") is None

