from src.utility.decorator import cors
import platform
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


@cors
@wsclient
def create_battle(event, context, wsclient):
    return app.create_battle(event, context, wsclient)

@cors
@wsclient
def get_battles(event, context, wsclient):
    return app.get_battles(event, context, wsclient)

@cors
@wsclient
def get_battle(event, context, wsclient):
    return app.get_battle(event, context, wsclient)


@cors
@wsclient
def start_battle(event, context, wsclient):
    return app.start_battle(event, context, wsclient)


@cors
@wsclient
def end_battle(event, context, wsclient):
    return app.end_battle(event, context, wsclient)


@cors
@wsclient
def start_round(event, context, wsclient):
    return app.start_round(event, context, wsclient)

@cors
@wsclient
def get_current_round(event, context, wsclient):
    return app.get_current_round(event, context, wsclient)


@cors
@wsclient
def end_round(event, context, wsclient):
    return app.end_round(event, context, wsclient)


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
    

def like_handler(event, context, wsclient):
    connection_id = event['requestContext']['connectionId']

    # DynamoDB에서 유저 정보 찾기
    response = dynamo_db.scan(
        TableName=config.DYNAMODB_WS_CONNECTION_TABLE,
        FilterExpression="connectionID = :connection_id",
        ExpressionAttributeValues={":connection_id": {"S": connection_id}},
        ProjectionExpression="battleID,connectionID,nickname,userID"
    )['Items']
    
    
    battle_id = response[0]['battleID']['S']
    user_id = json.loads(event['body'])['userId']
    order = json.loads(event['body'])['opinionNo']
    round = json.loads(event['body'])['round']
    
    # Opinion 테이블에서 해당 의견의 좋아요 수를 1증가 시킨다.
    # Race condition이 있기 때문에 쿼리를 동기화 해야한다.
    try:
        with PostgresContext(**config.db_config) as psql_ctx:
            with psql_ctx.cursor() as psql_cursor:
                psql_cursor.execute("BEGIN")
                psql_cursor.execute(f'SELECT "noOfLikes" FROM "Opinion" WHERE "userId" = \'{user_id}\' AND "battleId" = \'{battle_id}\' AND "roundNo" = {round} AND "order" = {order} FOR UPDATE;')
                row = psql_cursor.fetchone()      
                likes = row[0]
                psql_cursor.execute(f'UPDATE "Opinion" SET "noOfLikes" = {likes + 1} WHERE "userId" = \'{user_id}\' AND "battleId" = \'{battle_id}\' AND "roundNo" = {round} AND "order" = {order}')
                psql_cursor.execute("COMMIT;")
    except:
        wsclient.send(
            connection_id=connection_id,
            data={
                "action": "likeResult",
                "result": "fail",
                "opinionNo": order,
                "noOfLikes": "None"
            }
        )

        response = {
            'statusCode': 400,
            'body': 'Like Fail'
        }
        return response
    
    # Opinion 테이블에서 해당 의견의 좋아요 수를 가져온다.
    with PostgresContext(**config.db_config) as psql_ctx:
        with psql_ctx.cursor() as psql_cursor:

            select_query = f"""
                SELECT "noOfLikes"
                FROM "Opinion"
                WHERE "userId" = '{user_id}' AND "battleId" = '{battle_id}' AND "roundNo" = {round} AND "order" = {order}
            """
            psql_cursor.execute(select_query)
            row = psql_cursor.fetchall()
            no_of_likes = row[0][0]
    
    # Response 전송
    wsclient.send(
        connection_id=connection_id,
        data={
            "action": "likeResult",
            "result": "success",
            "opinionNo": order,
            "noOfLikes": no_of_likes
        }
    )

    response = {
        'statusCode': 200,
        'body': 'Like Success'
    }
    return response


@wsclient
def finish_battle_handler(event, context, wsclient):
    return app.finish_battle_handler(event, context, wsclient)
