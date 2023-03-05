from urllib.parse import parse_qs
import urllib.parse as urlparse
import requests
import json
import boto3
import botocore.errorfactory


def kakao_login(event, context):
    """
    Trying to login through Kakao account\n
    You should replace those things below\n
    - Kakao application: client_id(REST API Key), client_secret, redirect_uri\n
    - AWS Cognito: ClientId(User Pool application client ID)\n
    :return:
    """
    # Phase 1: Get authorized code from Kakao
    # parsed = urlparse.urlparse(request.full_path)
    # temp_code = parse_qs(parsed.query)['code']

    # From chatGPT:
    temp_code = event['code']
    print("Access code: ", temp_code)

    # Phase 2: Get access token from Kakao
    parameters = {
        'grant_type': 'authorization_code',
        'client_id': '${KAKAO_REST_API_KEY}',
        'client_secret': '${KAKAO_CLIENT_SECRET}',
        'redirect_uri': 'https://${CUSTOM_DOMAIN}/login/kakao',
        'code': temp_code
    }
    response = requests.post("https://kauth.kakao.com/oauth/token", params=parameters, verify=False)
    kakao_access_token = response.json()['access_token']
    # print("Access token: ", kakao_access_token)

    # Phase 3: Get user's email
    header = {'Authorization': f'Bearer {kakao_access_token}'}
    user_information = requests.get("https://kapi.kakao.com/v2/user/me", headers=header, verify=False).json()
    user_email = user_information['kakao_account']['email']
    # print(user_email)

    # Phase 4: Add user to Cognito User Pool
    client = boto3.client('cognito-idp', region_name='ap-northeast-2',
                          aws_access_key_id='${AWS_ACCESS_KEY}',
                          aws_secret_access_key='${AWS_ACCESS_SECRET}')
    try:
        client.admin_create_user(
            UserPoolId='ap-northeast-2_Gx5e0MS4K',
            Username=user_email,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': user_email
                }
            ]
        )
    except botocore.errorfactory.ClientError as client_error:
        if client_error.response['Error']['Code'] == "UsernameExistsException":
            print("Already signed with Kakao!")
        else:
            raise client_error

    body = {
        "message": "Hello! Your email is %s" % user_email,
        "input": event
    }

    return {"statusCode": 200, "body": json.dumps(body)}
