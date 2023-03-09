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
    :return: Response for Kakao login.
    """

    # Get authorized code from Kakao
    access_code = event['queryStringParameters']['code']
    email, nickname = kakao.get_properties(access_code)
    # print("Before sign-in, email:", email)

    # Sign in to cognito user pool. And get ID token.
    # If user name is not in user pool, do sign-up first.
    id_token = cognito.sign_in(email, nickname)

    # Exchange ID token for temporary credentials.
    temp_credentials = cognito.get_temp_cred(id_token)

    # return email, nickname and temp_credentials for test
    return {
        "statusCode": 200,
        "body": json.dumps({
            'email': email,
            'nickname': nickname,
            'temp-cred': {
                'SessionToken': temp_credentials['SessionToken'],
                'Expiration': temp_credentials['Expiration'].strftime("%Y-%m-%d %H:%M:%S")
            }
        })
    }
