import boto3
import psycopg2
import pytest
from redis import Redis

from src.utility.context import RedisContext
from src.game.config import *

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

@pytest.fixture
def dynamo_db():
    client = boto3.resource(**dynamo_db_config)
    yield client


def test_redis_get_client(redis):
    my_client = redis.client_info()
    assert my_client['id'] is not None, "Redis Connection Failed"


def test_psycopg2_connection(db):
    assert db is not None, "Psycopg2 Connection Failed"


def test_dynamodb_connection(dynamo_db):
    assert dynamo_db is not None, "DynamoDB Connection Failed"
