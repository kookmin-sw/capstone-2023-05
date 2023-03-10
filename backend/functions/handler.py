import json
import tqdm
import requests
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
    email = kakao.get_email(access_code)

    # TODO: It has two situations. One is email is not in cognito pool. The other is email is in cognito pool.
    # When email is already in pool, we don't have to show under html!
    # How can we figure this?

    # Show this html to getting user's nickname
    get_nickname_html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Enter your nickname</title>
        </head>
        <body>
            <p>Your Email: %s</p>
            <p>Enter your nickname below</p>
            <form>
                <label for="nickname">Nickname:</label>
                <input type="text" id="nickname" name="nickname"><br><br>
                <input type="button" value="Continue" onclick="submitNickname()">
            </form>

            <script>
                function submitNickname() {
                    // get the nickname from the input field
                    var nickname = document.getElementById("nickname").value;

                    // do something with the nickname, like redirect to a new page
                    window.location.href = "http://localhost:3000/dev/login/cognito?email=%s&nickname=" + nickname;
                }
            </script>
        </body>
    </html>
    """ % (email, email)

    return {
        "statusCode": 302,
        "body": get_nickname_html,
        "headers": {"Content-Type": "text/html"}
    }


def cognito_login(event, context):
    # TODO: Create a simple page for getting user's nickname
    # 3. How can I redirect from html to my function with user's input?
    email = event['queryStringParameters']['email']
    nickname = event['queryStringParameters']['nickname']

    # Sign in to cognito user pool. And get ID token.
    # If user name is not in user pool, do sign-up first.
    id_token = cognito.sign_in(email, nickname, "Kakao")

    # Exchange ID token for temporary credentials.
    temp_credentials = cognito.get_temp_cred(id_token, "Kakao")

    # return email, nickname and temp_credentials for test
    return {
        "statusCode": 200,
        "body": json.dumps({
            'email': email,
            'nickname': nickname,
            'temp-cred': json.dumps(temp_credentials)
        })
    }


# def google_login(event, context):
#     # TODO: How to get ID token? It is on the redirect url, but token is not in queryParameters!
#     # print(event)

#     # temp_credentials = cognito.get_temp_cred(google_id_token, "Google")

#     return {
#         "statusCode": 200,
#         "body": "Hello Google!"
#     }