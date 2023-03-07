import json
import tqdm
import boto3
import auth.kakao as kakao


def hello(event, context):
    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
    }

    tqdm.tqdm()

    return {"statusCode": 200, "body": json.dumps(body)}


def kakao_login(event, context):
    """
    Trying to login through Kakao account\n
    :return:
    """

    # Get authorized code from Kakao
    access_code = event['queryStringParameters']['code']
    email, nickname = kakao.get_properties(access_code)

    # Phase 4: Add user to Cognito User Pool
    client = boto3.client('cognito-idp', region_name='ap-northeast-2',
                          aws_access_key_id='${AWS_ACCESS_KEY}',
                          aws_secret_access_key='${AWS_ACCESS_SECRET}')


    # return email and nickname for test
    return {
        "statusCode": 200,
        "body": json.dumps({
            'email': email,
            'nickname': nickname
        })
    }
