import json
import os
import requests
import auth.kakao as kakao
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
                        window.location.href = "http://localhost:3000/dev/login/cognito?email=%s&nickname=" + nickname + "&newuser=%d";
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
            "email": email,
            "nickname": nickname,
            "newuser": 0
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

    email = event['queryStringParameters']['email']
    nickname = event['queryStringParameters']['nickname']
    is_newbie = event['queryStringParameters']['newuser']

    # If user is newbie, set nickname
    if is_newbie:
        cognito.set_nickname(email, nickname)

    cognito_auth = cognito.get_token(email)

    # Exchange ID token for temporary credentials.
    temp_credentials = cognito.get_temp_cred(cognito_auth['IdToken'], "Kakao")
    expire_time = temp_credentials['Expiration']
    temp_credentials['Expiration'] = expire_time.strftime("%Y-%m-%d %H:%M:%S")

    # return email, nickname and temp_credentials for test
    return {
        "statusCode": 200,
        "body": json.dumps({
            'email': email,
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

    
def google_login(event, context):
    # TODO: How can I change code to id token?
    # temp_credentials = cognito.get_temp_cred(google_id_token, "Google")
    google_code = event['queryStringParameters']['code']
    body = {
        "grant_type": "authorization_code",
        "code": google_code,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": "http://localhost:3000/dev/login/cognito"
    }
    response = requests.post("https://oauth2.googleapis.com/token", data=body)
    print(response.content)

    return {
        "statusCode": 200,
        "body": google_code
    }