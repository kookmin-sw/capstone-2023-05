import json
import tqdm
import auth.kakao as kakao
import auth.cognito as cognito


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
    print("Before sign-in, email:", email)

    access_token = cognito.sign_in(email, nickname)
    print("After sign-in, email:", email)

    # return email, nickname and access_code for test
    return {
        "statusCode": 200,
        "body": json.dumps({
            'email': email,
            'nickname': nickname,
            'access-token': access_token
        })
    }
