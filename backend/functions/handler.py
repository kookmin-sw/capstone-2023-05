import json
import tqdm
import os
import auth.kakao as kakao
import auth.cognito as cognito


def login(event, context):
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
                        window.location.href = "https://naruhodoo-test.auth.ap-northeast-2.amazoncognito.com/login?response_type=token&client_id=%s&redirect_uri=%s";
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
    # If user email is not in user pool, do sign-up first.
    cognito_auth_info, nickname, is_newbie = cognito.sign_in(email, "Kakao")
    cognito_id_token = cognito_auth_info['IdToken']
    cognito_refresh_token = cognito_auth_info['RefreshToken']

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
                        window.location.href = "http://localhost:3000/dev/login/cognito?email=%s&nickname=" + nickname + "&token=%s&refresh=%s&newuser=%d";
                    }
                </script>
            </body>
        </html>
        """ % (email, nickname, email, cognito_id_token, cognito_refresh_token, 1)

        return {
            "statusCode": 302,
            "body": get_nickname_html,
            "headers": {"Content-Type": "text/html"}
        }
    else:
        # Show this html to redirecting
        redirect_html = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>You already have account!</title>
            </head>
            <body>
                <h1>Your Account</h1>
                <li> email: %s</li>
                <li> nickname: %s</li>
                <p>
                    <a href="http://localhost:3000/dev/login/cognito?email=%s&nickname=%s&token=%s&refresh=%s&newuser=%d">Continue with your account</a>
                </p>
            </body>
        </html>
        """ % (email, nickname, email, nickname, cognito_id_token, cognito_refresh_token, 0)

        return {
            "statusCode": 302,
            "body": redirect_html,
            "headers": {"Content-Type": "text/html"}
        }
    

def cognito_login(event, context):
    email = event['queryStringParameters']['email']
    nickname = event['queryStringParameters']['nickname']
    id_token = event['queryStringParameters']['token']
    refresh_token = event['queryStringParameters']['refresh']
    is_newbie = event['queryStringParameters']['newuser']

    # If user is new, set nickname
    if is_newbie:
        cognito.set_nickname(email, nickname)

    # Exchange ID token for temporary credentials.
    temp_credentials = cognito.get_temp_cred(id_token, "Kakao")
    expire_time = temp_credentials['Expiration']
    temp_credentials['Expiration'] = expire_time.strftime("%Y-%m-%d %H:%M:%S")

    # return email, nickname and temp_credentials for test
    return {
        "statusCode": 200,
        "body": json.dumps({
            'email': email,
            'nickname': nickname,
            'cognito-refresh': refresh_token,
            'temp-cred': json.dumps(temp_credentials)
        })
    }


# TODO: Question! Do I have to control about tokens?
def logout(event, context):
    # I need refresh token from cognito. And refresh token will be in body.
    # But GET method does not have body! How about header?
    cognito.block_token(event['queryStringParameters']['refresh-token'])

    # Redirect to login page
    return {
        'statusCode': 302,
        'headers': {'Location': 'http://localhost:3000/dev/login'}
    }


def delete_account(event, context):
    cognito.block_token(event['refresh-token'])
    cognito.delete_account(event['email'])

    
def google_login(event, context):
    # TODO: How to get ID token? Access token is on the redirect url, but token is not in queryParameters!
    # temp_credentials = cognito.get_temp_cred(google_id_token, "Google")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "input": event,
            "message": "Login from Google!"
        })
    }