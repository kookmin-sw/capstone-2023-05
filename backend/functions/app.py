from urllib.parse import parse_qs
import urllib.parse as urlparse
import requests
import json
import boto3
import botocore.errorfactory
import auth.kakao as kakao 


def kakao_login(event, context):
    """
    Trying to login through Kakao account\n
    You should replace those things below\n
    - Kakao application: client_id(REST API Key), client_secret, redirect_uri\n
    - AWS Cognito: ClientId(User Pool application client ID)\n
    :return:
    """

    #Get authorized code from Kakao
    access_code = event['queryStringParameters']['code']
    email = kakao.get_email(access_code)

    # return email for test
    return {
       "statusCode": 200,
        "body": json.dumps(email)
    }

    # return {"statusCode": 200, "body": json.dumps(email)}

    # # Phase 4: Add user to Cognito User Pool
    # client = boto3.client('cognito-idp', region_name='ap-northeast-2',
    #                       aws_access_key_id='${AWS_ACCESS_KEY}',
    #                       aws_secret_access_key='${AWS_ACCESS_SECRET}')
    # try:
    #     client.admin_create_user(
    #         UserPoolId='ap-northeast-2_Gx5e0MS4K',
    #         Username=user_email,
    #         UserAttributes=[
    #             {
    #                 'Name': 'email',
    #                 'Value': user_email
    #             }
    #         ]
    #     )
    # except botocore.errorfactory.ClientError as client_error:
    #     if client_error.response['Error']['Code'] == "UsernameExistsException":
    #         print("Already signed with Kakao!")
    #     else:
    #         raise client_error

    # body = {
    #     "message": "Hello! Your email is %s" % user_email,
    #     "input": event
    # }

    # return {"statusCode": 200, "body": json.dumps(body)}
