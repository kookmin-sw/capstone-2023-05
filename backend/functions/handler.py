import json
import tqdm
import requests


def hello(event, context):
    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
    }

    tqdm.tqdm()

    return {"statusCode": 200, "body": json.dumps(body)}


def show_kakao_login(event, context):
    """
    Trying to login through Kakao account\n
    You should replace those things below\n
    - Kakao application: client_id(REST API Key), client_secret, redirect_uri\n
    - AWS Cognito: ClientId(User Pool application client ID)\n
    :return:
    """

    # Read under site
    # https://www.linkedin.com/pulse/serverless-websites-aws-using-lambda-api-gateway-part-skultety

    # Just giving Kakao login url
    response = requests.get("https://kauth.kakao.com/oauth/authorize?client_id=${KAKAO_REST_API_KEY}&redirect_uri=http://${CUSTOM_DOMAIN}/callback&response_type=code")
    return {
        "statusCode": 200,
        "body": response.content.decode()
    }
