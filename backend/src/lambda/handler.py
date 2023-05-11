import json
import os
import boto3

from src.auth import kakao, google, cognito

from src.utility.decorator import cors


s3 = boto3.client('s3')
# Getting fragment information from browser!
# So, let's make a empty html page for redirecting here
# Getting fragment, checking user is new user or not
# And redirect to setting nickname page or lobby page.

@cors
def login(event, context):
    response = s3.get_object(Bucket='jwlee-test-bucket', Key='login.html')
    content = response['Body'].read().decode('utf-8')
    return {
        'statusCode': 200,
        'body': content,
        'headers': {'Content-Type': 'text/html'}
    }


@cors
def kakao_process(event, context):
    response = s3.get_object(Bucket='jwlee-test-bucket/kakao_process', Key='kakao_process.html')
    content = response['Body'].read().decode('utf-8')
    return {
        'statusCode': 200,
        'body': content,
        'headers': {'Content-Type': 'text/html'}
    }


@cors
def google_process(event, context):
    response = s3.get_object(Bucket='jwlee-test-bucket/google_process', Key='google_process.html')
    content = response['Body'].read().decode('utf-8')
    return {
        'statusCode': 200,
        'body': content,
        'headers': {'Content-Type': 'text/html'}
    }


@cors
def nickname(event, context):
    response = s3.get_object(Bucket='jwlee-test-bucket/nickname', Key='nickname.html')
    content = response['Body'].read().decode('utf-8')
    return {
        'statusCode': 200,
        'body': content,
        'headers': {'Content-Type': 'text/html'}
    }


@cors
def kakao_login(event, context):
    """
    Trying to login through Kakao account\n
    :return: Response for Kakao login.
    """

    # Get authorized code from Kakao
    access_code = event['queryStringParameters']['code']
    email = kakao.get_email(access_code)

    # Sign in to cognito user pool. And get ID token.
    is_newbie = cognito.sign_in(email, "Kakao")
    cognito_auth = cognito.get_token(email)
    access_token = cognito_auth['AccessToken']

    return {
        'statusCode': 302,
        'headers': {'Location': f'http://localhost:3000/{os.getenv("PRIVATE_STAGE")}/login/process?email={email}&newbie={is_newbie}&token={access_token}'}
    }


@cors
def google_login(event, context):
    # How to get user's google account? => Get token from code and decode the token    
    return {
        'statusCode': 200,
        'body': "Hello"
    }

    # cognito_user_name = cognito.get_username(google_email)
    # idp_client = boto3.client('cognito-idp', region_name='ap-northeast-2')
    # response = idp_client.list_users(
    #     UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID")
    # )

    # nickname = "TempNickname"
    # for user in response['Users']:
    #     if cognito_user_name == user['Username']:
    #         for attr in user['Attributes']:
    #             # If user logged in from Kakao, nickname will be exist
    #             # Else if user logged in from Google, he doesn't have nickname
    #             # So find from email attribute
    #             if attr['Name'] == "nickname":
    #                 nickname = attr['Value']
    #                 break

    #         parameters = {
    #             "username": cognito_user_name,
    #             "nickname": nickname,
    #             "newuser": 0,
    #             "provider": "google"
    #         }
    #         auth_result = requests.get("http://localhost:3000/dev/login/cognito", params=parameters).json()
    #         return {
    #             'statusCode': 200,
    #             'body': json.dumps(auth_result)
    #         }    

    # # If user is newbie to our service, get nickname from user.
    # get_nickname_html = """
    # <!DOCTYPE html>
    # <html>
    #     <head>
    #         <title>Enter your nickname</title>
    #     </head>
    #     <body>
    #         <p>Your e-mail: %s</p>
    #         <p>Your current nickname: %s</p>
    #         <p>Enter your nickname below</p>
    #         <form>
    #             <label for="nickname">New nickname:</label>
    #             <input type="text" id="nickname" name="nickname"><br><br>
    #             <input type="button" value="Continue" onclick="submitNickname()">
    #         </form>

    #         <script>
    #             function submitNickname() {
    #                 // get the nickname from the input field
    #                 var nickname = document.getElementById("nickname").value;

    #                 // do something with the nickname, like redirect to a new page
    #                 window.location.href = "http://localhost:3000/dev/login/cognito?username=%s&nickname=" + nickname + "&newuser=%d";
    #             }
    #         </script>
    #     </body>
    # </html>
    # """ % (google_email, nickname, cognito_user_name, 1)

    # return {
    #     "statusCode": 200,
    #     "body": get_nickname_html,
    #     "headers": {"Content-Type": "text/html"}
    # }
    

@cors
def cognito_login(event, context):
    """
    Trying to get access token from aws cognito.\n
    And getting temporary aws credentials.\n
    :return: Response for getting credentials.
    """

    user_name = event['queryStringParameters']['username']
    nickname = event['queryStringParameters']['nickname']
    provider = event['queryStringParameters']['provider']

    cognito_auth = cognito.get_token(user_name)
    if provider == "kakao":
        # Exchange ID token for temporary credentials.
        temp_credentials = cognito.get_temp_cred(cognito_auth['IdToken'], "Kakao")
    else:
        # Get temporary credentials with google user name.
        temp_credentials = google.get_temp_cred(user_name)
    temp_credentials['Expiration'] = temp_credentials['Expiration'].strftime("%Y-%m-%d %H:%M:%S")

    # return user name, nickname, authentication information for cognito and temp aws credentials for test
    return {
        "statusCode": 200,
        "body": json.dumps({
            'email': user_name,
            'nickname': nickname,
            'cognito-authentication': cognito_auth,
            'temp-cred': temp_credentials
        })
    }


@cors
def logout(event, context):
    """
    Trying to sign out via cognito.\n
    :return: Redirect to login html
    """

    access_token = event['headers']['Authorization']
    cognito.sign_out(access_token)

    # Redirect to login page
    return {
        'statusCode': 302,
        'headers': {'Location': f'http://localhost:3000/{os.getenv("PRIVATE_STAGE")}/login'},
    }


@cors
def delete_account(event, context):
    """
    Trying to delete user in cognito user pool.\n
    :return: Response for deleting user.
    """

    cognito.delete_account(json.loads(event['body'])['email'])

    return {
        'statusCode': 200,
        'body': "Completely deleted your account from AWS Cognito."
    }
