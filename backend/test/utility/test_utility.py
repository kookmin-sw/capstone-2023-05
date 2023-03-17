import os
import psycopg2
import pytest
from redis import Redis

from src.utility.context import RedisContext
from src.game.config import redis_config, db_config

from logging import getLogger

log = getLogger(__name__)


@pytest.fixture
def db():
    client = psycopg2.connect(**db_config)
    yield client
    client.close()


@pytest.fixture
def redis() -> Redis:
    ctx = RedisContext(**redis_config)
    yield ctx.client
    ctx.client.close()


def test_redis_get_client(redis):
    my_client = redis.client_info()
    assert my_client['id'] is not None, "Redis Connection Failed"

def test_psycopg2_connection(db):
    assert db is not None, "Psycopg2 Connection Failed"



if __name__ == "__main__":
    print(db_config)