import pytest
import os

from logging import getLogger

from src.utility.redis import RedisHelper

log = getLogger(__name__)

@pytest.fixture
def redis_info() -> tuple:
    host = os.environ.get("REDIS_HOST", "localhost")
    port = os.environ.get("REDIS_PORT", '6379')
    db = os.environ.get("REDIS_DB", '0')
    return host, port, db


def test_redis_get_client(redis_info):
    with RedisHelper(*redis_info) as redis:
        my_client = redis.client_info()
        assert my_client['id'] is not None
        log.debug(f"Redis client info: {my_client}")