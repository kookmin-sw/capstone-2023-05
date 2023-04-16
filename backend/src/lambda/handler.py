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
def create_battle(event, context):
    """
        HTTP Method: POST
        Creates new battle
    """
    return app.create_battle(event, context)

@cors
def get_battles(event, context):
    """
        HTTP Method: GET
        Get all the battles info
    """
    return app.get_battles(event, context)

@cors
def get_battle(event, context):
    """
        HTTP Method: PUT
        Update battle
    """
    return app.get_battle(event, context)

@cors
def start_battle(event, context):
    """
        HTTP Method: PUT
        
        Starts Battle and sets battle status as RUNNING
    """ 
    return app.start_battle(event, context)

@cors
def end_battle(event, context):
    """
        HTTP METHOD: PUT
        Ends Battle and sets battle status as CLOSED
    """
    return app.end_battle(event, context)

@cors
def start_round(event, context):
    """
        HTTP METHOD: PUT
        Starts Round 
    """
    return app.start_round(event, context)

@cors
def end_round(event, context):
    """
        HTTP METHOD: PUT
        Ends Round 
    """
    return app.end_round(event, context)


