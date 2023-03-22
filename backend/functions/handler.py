import json
import os
import requests
import boto3
import auth.kakao as kakao
import auth.google as google
import auth.cognito as cognito


def login(event, context):
    """
    Showing login page.\n
    :return: Response for getting login html
    """

    login_html = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Naruhodoo Login</title>
            </head>
            <body>
                <h1>Let's start with your account!</h1>
                <form>
                    <input type="button" value="Log-in with Kakao" onclick="loginKakao()">
                    <input type="button" value="Log-in with Google" onclick="loginGoogle()">
                </form>

                <script>
                    function loginKakao() {
                        // do something with the nickname, like redirect to a new page
                        window.location.href = "https://kauth.kakao.com/authorize?response_type=code&client_id=%s&redirect_uri=%s";
                    }
                    function loginGoogle() {
                        window.location.href = "https://naruhodoo-test.auth.ap-northeast-2.amazoncognito.com/login?response_type=code&client_id=%s&redirect_uri=%s";
                    }
                </script>
            </body>
        </html>
        """ % (os.getenv("KAKAO_REST_API_KEY"), "http://localhost:3000/dev/login/kakao", os.getenv("AWS_COGNITO_CLIENT_ID"), "http://localhost:3000/dev/login/google")
    
    return {
            "statusCode": 200,
            "body": login_html,
            "headers": {"Content-Type": "text/html"}
        }


def google_login(event, context):
    # How to set nickname to new user?
    # No idea to get email with google code?
    # google_email = event['queryStringParameters']['email']
    code = event['queryStringParameters']['code']
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': "Hello Google"
        })
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


def kakao_login(event, context):
    """
    Trying to login through Kakao account\n
    :return: Response for Kakao login.
    """

    # Get authorized code from Kakao
    access_code = event['queryStringParameters']['code']
    email = kakao.get_email(access_code)

    # Sign in to cognito user pool. And get ID token.
    nickname, is_newbie = cognito.sign_in(email, "Kakao")

    # If user is newbie to our service, get nickname from user.
    if is_newbie:
        # Show this html to getting user's nickname
        get_nickname_html = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Enter your nickname</title>
            </head>
            <body>
                <p>Your e-mail: %s</p>
                <p>Your current nickname: %s</p>
                <p>Enter your nickname below</p>
                <form>
                    <label for="nickname">New nickname:</label>
                    <input type="text" id="nickname" name="nickname"><br><br>
                    <input type="button" value="Continue" onclick="submitNickname()">
                </form>

                <script>
                    function submitNickname() {
                        // get the nickname from the input field
                        var nickname = document.getElementById("nickname").value;

                        // do something with the nickname, like redirect to a new page
                        window.location.href = "http://localhost:3000/dev/login/cognito?username=%s&nickname=" + nickname + "&newuser=%d&provider=kakao";
                    }
                </script>
            </body>
        </html>
        """ % (email, nickname, email, 1)

        return {
            "statusCode": 200,
            "body": get_nickname_html,
            "headers": {"Content-Type": "text/html"}
        }
    else:
        parameters = {
            "username": email,
            "nickname": nickname,
            "newuser": 0,
            "provider": "kakao"
        }
        auth_result = requests.get("http://localhost:3000/dev/login/cognito", params=parameters).json()
        return {
            'statusCode': 200,
            'body': json.dumps(auth_result)
        }
    

def cognito_login(event, context):
    """
    Trying to get access token from aws cognito.\n
    And getting temporary aws credentials.\n
    :return: Response for getting credentials.
    """

    user_name = event['queryStringParameters']['username']
    nickname = event['queryStringParameters']['nickname']
    is_newbie = event['queryStringParameters']['newuser']
    provider = event['queryStringParameters']['provider']

    # If user is newbie, set nickname
    if is_newbie:
        cognito.set_nickname(user_name, nickname)

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
        'headers': {'Location': 'http://localhost:3000/dev/login'},
    }


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
