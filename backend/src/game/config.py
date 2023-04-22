import os

redis_config = {
    "host": os.getenv("REDIS_HOST"),
    "port": os.getenv("REDIS_PORT"),
    "db": os.getenv("REDIS_DB")
}

db_config = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DB")
}

dynamo_db_config = {
    "service_name": "dynamodb",
    "endpoint_url": os.getenv("DYNAMODB_ENDPOINT") if os.getenv("IS_OFFLINE") == "true" else None,
}

DYNAMODB_WS_CONNECTION_TABLE = os.getenv("DYNAMODB_WS_CONNECTION_TABLE")