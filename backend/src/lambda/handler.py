import json
import platform
import os
import time
from datetime import datetime
import boto3

from src.game import app
from src.utility.context import PostgresContext


dynamo_db = boto3.client('dynamodb')
psql_ctx = PostgresContext(os.getenv("POSTGRES_HOST"), os.getenv("POSTGRES_PORT"), os.getenv("POSTGRES_USER"),
                               os.getenv("POSTGRES_PASSWORD"), os.getenv("POSTGRES_DB"))
psql_cursor = psql_ctx.cursor


def hello(event, context):
    msg = app.hello()
    response = {
        "statusCode": 200,
        "body": msg
    }
    return response


def get_platform(event, context):
    msg = platform.platform()
    response = {
        "statusCode": 200,
        "body": msg
    }
    return response


def hello_redis(event, context):
    client_info = app.hello_redis()
    response = {
        "statusCode": 200,
        "body": json.dumps(client_info)
    }
    return response


def hello_db(event, context):
    msg = app.hello_db()
    response = {
        "statusCode": 200,
        "body": msg
    }
    return response


def connect_handler(event, context):
    # 기존에 원스텝이었던 것을 투스텝으로 쪼개자.
    # 여기서는 말 그대로 websocket 길만 뚫어준다.
    return {
        'statusCode': 200,
        'body': json.dumps({"message": "Connect Success"})
    }


def disconnect_handler(event, context):
    connection_id = event['requestContext']['connectionId']

    # Find request user's battle id
    response = dynamo_db.scan(
        TableName="websocket-connections-jwlee-test",
        FilterExpression="connectionID = :connection_id",
        ExpressionAttributeValues={":connection_id": {"S": connection_id}},
        ProjectionExpression="battleID,connectionID"
    )['Items']
    battle_id = response[0]['battleID']['S']
    
    dynamo_db.delete_item(
        TableName="websocket-connections-jwlee-test",
        Key={
            'battleID': {'S': battle_id},
            'connectionID': {'S': connection_id}
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': "Delete connection from DB"})
    }


def init_join_handler(event, context):
    connection_id = event['requestContext']['connectionId']

    # 데이터를 header로 보내는 경우
    headers = event['headers']
    battle_id = headers['battleId']
    nickname = headers['nickname']
    user_id = headers['userId']
    team_id = ""
    
    # 데이터를 queryStringParameter로 보내는 경우
    # parameters = event['queryStringParameters']
    # battle_id = parameters['battleId']
    # nickname = parameters['nickname']
    # user_id = parameters['userId']
    # team_id = ""

    # DynamoDB에 정보 등록
    dynamo_db.put_item(
        TableName="websocket-connections-jwlee-test",
        Item={
            'connectionID': {'S': connection_id},
            'battleID': {'S': battle_id},
            'teamID': {'S': team_id},
            'userID': {'S': user_id},
            'nickname': {'S': nickname}
        }
    )

    # 어떤 팀이 있는지 RDS에서 정보 가져오기
    select_query = f"SELECT name FROM \"Team\" WHERE \"battleId\" = {battle_id}"
    psql_cursor.execute(select_query)
    rows = psql_cursor.fetchall()
    psql_cursor.close()
    team_names = [row for row in rows]

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Join Request Success',
            'teams': team_names
        })
    }


def send_handler(event, context):
    opinion_time = datetime.fromtimestamp(time.time())
    
    # DynamoDB의 모든 값을 얻어온다.
    paginator = dynamo_db.get_paginator('scan')
    connections = []
    for page in paginator.paginate(TableName="websocket-connections-jwlee-test"):
        connections.extend(page['Items'])

    my_connection_id = event['requestContext']['connectionId']

    # 사용자의 connection 정보를 찾는다.
    my_info = None
    for connection in connections:
        if connection['connectionID']['S'] == my_connection_id:
            my_info = connection
            break
    if my_info is None:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': "Cannot find your connection information"})
        }
    
    apigatewaymanagementapi = boto3.client(
        'apigatewaymanagementapi',
        endpoint_url=f"https://{event['requestContext']['domainName']}/{event['requestContext']['stage']}"
    )
    
    # 같은 팀에게 자신의 의견을 broadcasting 한다.
    opinion = json.loads(event['body'])['opinion']
    user_id, battle_id, team_id, nickname = my_info['userID']['S'], my_info['battleID']['S'], my_info['teamID']['S'], my_info['nickname']['S']
    for connection in connections:
        other_connection = connection['connectionID']['S']
        if connection['battleID']['S'] == battle_id and connection['teamID']['S'] == team_id:
            apigatewaymanagementapi.post_to_connection(
                Data=nickname + ": " + opinion,
                ConnectionId=other_connection
            )

    # PK: userId, battleId, roundNo, time
    # extra fields: noOfLikes, content, status
    round, num_of_likes = json.loads(event['body'])['round'], 0
    status = "CANDIDATE"

    insert_query = f'INSERT INTO \"Opinion\" VALUES ({user_id}, {battle_id}, {round}, {opinion_time}, {num_of_likes}, {opinion}, {status})'
    psql_cursor.execute(insert_query)
    psql_ctx.client.commit()
    psql_cursor.close()

    return {
        'statusCode': 200,
        'body': json.dumps({'message': "Post your opinion to your team"})
    }