import json
import tqdm
import boto3
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

    # Sign in to cognito user pool. And get ID token.
    # If user email is not in user pool, do sign-up first.
    cognito_id_token, nickname, is_newbie = cognito.sign_in(email, "Kakao")

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
                        window.location.href = "http://localhost:3000/dev/login/cognito?email=%s&nickname=" + nickname + "&token=%s";
                    }
                </script>
            </body>
        </html>
        """ % (email, nickname, email, cognito_id_token)

        return {
            "statusCode": 302,
            "body": get_nickname_html,
            "headers": {"Content-Type": "text/html"}
        }
    else:
        return {
            "statusCode": 302,
            "headers": {"Location": "http://localhost:3000/dev/login/cognito?email=%s&nickname=%s&token=%s" % (email, nickname, cognito_id_token)}
        }

def cognito_login(event, context):
    email = event['queryStringParameters']['email']
    nickname = event['queryStringParameters']['nickname']    # Will be same as email
    id_token = event['queryStringParameters']['token']

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