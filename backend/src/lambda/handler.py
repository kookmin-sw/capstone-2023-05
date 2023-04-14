from src.game import app
from src.utility.decorator import cors
import platform
import os


@cors
def hello(event, context):
    msg = app.hello()
    response = {
        "statusCode": 200,
        "body": msg
    }
    return response


@cors
def get_platform(event, context):
    msg = platform.platform()
    response = {
        "statusCode": 200,
        "body": msg
    }
    return response


@cors
def hello_redis(event, context):
    client_info = app.hello_redis()
    response = {
        "statusCode": 200,
        "body": json.dumps(client_info)
    }
    return response


@cors
def hello_db(event, context):
    msg = app.hello_db()
    response = {
        "statusCode": 200,
        "body": msg
    }
    return response


@cors
def create_room(event, context):
    return app.create_room(event, context)

@cors
def get_room(event, context):
    return app.get_room(event, context)

