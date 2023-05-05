import json
import platform

from src.game import app

from src.utility.decorator import cors
from src.utility.websocket import wsclient


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


def connect_handler(event, context):
    return app.connect_handler(event, context)


def disconnect_handler(event, context):
    return app.disconnect_handler(event, context)


@wsclient
def init_join_handler(event, context, wsclient):
    return app.init_join_handler(event, context, wsclient)
    

@wsclient
def send_handler(event, context, wsclient):
    return app.send_handler(event, context, wsclient)


@wsclient
def vote_handler(event, context, wsclient):
    return app.vote_handler(event, context, wsclient)


@wsclient
def preparation_start_handler(event, context, wsclient):
    return app.preparation_start_handler(event, context, wsclient)
    