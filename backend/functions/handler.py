import json
import os
import requests
import boto3
import auth.kakao as kakao
import auth.google as google
import auth.cognito as cognito


# Getting fragment information from browser!
# So, let's make a empty html page for redirecting here
# Getting fragment, checking user is new user or not
# And redirect to setting nickname page or lobby page.

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
                    // redirect to a new page
                    function loginKakao() {
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


def process(event, context):
    process_html ="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Redirecting...</title>
        <script src="https://sdk.amazonaws.com/js/aws-sdk-2.815.0.min.js"></script>
        <script>
            // Retrieve query parameters from URL
            const queryString = window.location.search;
            const urlParams = new URLSearchParams(queryString);
            const email = urlParams.get('email');
            const newbie = urlParams.get('newbie');
            const cognitoAccessToken = urlParams.get('token');

            console.log(email); console.log(newbie); console.log(cognitoAccessToken);


            // Redirect to the specified URL
            if (newbie == 1) {
                window.location.href = "http://localhost:3000/dev/profile/nickname?email=" + email + "&token=" + cognitoAccessToken;
            }
            else {
                 // Set the region and credentials for your AWS account
                AWS.config.update({
                    region: 'ap-northeast-2',
                    credentials: new AWS.CognitoIdentityCredentials({
                        IdentityPoolId: 'ap-northeast-2:e40d2c07-62f3-4247-bc5c-1ac67f77db12'
                    })
                });

                // Create an instance of the CognitoIdentityServiceProvider class
                var cognitoIdP = new AWS.CognitoIdentityServiceProvider();

                

                // Call the listUsers method to retrieve a list of users
                function getNicknameByEmail(email, callback) {
                    // Set the parameters for the listUsers method
                    var params = {
                        UserPoolId: 'ap-northeast-2_pWsRKg63G',
                        AttributesToGet: ['email', 'nickname'],
                        Limit: 50
                    };

                    cognitoIdP.listUsers(params, function(err, data) {
                        if (err) {
                            console.log(err, err.stack);
                        } else {
                            const userList = data.Users;
                            console.log(data.Users);

                            var nickname;
                            for (var i = 0; i < userList.length; i++) {
                                if (userList[i].Attributes[0].Value == email) {
                                    console.log(userList[i].Attributes[1].Value)
                                    nickname = userList[i].Attributes[1].Value;
                                }
                            }

                            callback(nickname);
                        }
                    });
                }

                getNicknameByEmail(email, function(nickname) {
                    window.location.href = "http://localhost:3000/dev/login/cognito?username=" + email + "&nickname=" + nickname + "&provider=Kakao";
                });
            }
        </script>
    </head>
    </html>
    """
    return {
        "statusCode": 200,
        "body": process_html,
        "headers": {"Content-Type": "text/html"}
    }


def nickname(event, context):
    # TODO: Why nickname is 'undefined'?
    
    nickname_html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Enter your nickname</title>
            <script src="https://sdk.amazonaws.com/js/aws-sdk-2.815.0.min.js"></script>
        </head>
        <body>
            <p>Enter your nickname below</p>
            <form>
                <label for="nickname">New nickname:</label>
                <input type="text" id="nickname" name="nickname"><br><br>
                <input type="button" value="Continue" onclick="submitNickname()">
            </form>

            <script>
                const queryString = window.location.search;
                const urlParams = new URLSearchParams(queryString);
                const email = urlParams.get('email');
                const cognitoAccessToken = urlParams.get('token');

                // Set the region and credentials for your AWS account
                AWS.config.update({
                    region: 'ap-northeast-2',
                    credentials: new AWS.CognitoIdentityCredentials({
                        IdentityPoolId: 'ap-northeast-2:e40d2c07-62f3-4247-bc5c-1ac67f77db12'
                    })
                });

                // Create an instance of the CognitoIdentityServiceProvider class
                var cognitoIdP = new AWS.CognitoIdentityServiceProvider();

                // Call the listUsers method to retrieve a list of users
                function getNameByEmail(email, callback) {
                    // Set the parameters for the listUsers method
                    var params = {
                        UserPoolId: 'ap-northeast-2_pWsRKg63G',
                        AttributesToGet: ['email'],
                        Limit: 50
                    };
                    
                    cognitoIdP.listUsers(params, function(err, data) {
                        if (err) {
                            console.log(err, err.stack);
                        } else {
                            const userList = data.Users;
                            var name;
                            for (var i = 0; i < userList.length; i++) {
                                if (userList[i].Username == email){
                                    name = userList[i].Username;
                                    break;
                                }
                                else if (userList[i].Attributes[0].Value == email) {
                                    console.log(userList[i].Attributes[0].Value)
                                    name = userList[i].Username;
                                    break;
                                }
                            }

                            callback(name);
                        }
                    });
                }
                
                function submitNickname() {
                    // get the nickname from the input field
                    const userNickname = document.getElementById("nickname").value;

                    getNameByEmail(email, function(name) {
                        var params = {
                            AccessToken: cognitoAccessToken,
                            UserAttributes: [{
                                Name: 'nickname',
                                Value: userNickname
                            }]
                        };
                        cognitoIdP.updateUserAttributes(params, function(err, data) {
                            if (err) {
                                console.log(err);
                            }
                        });
                    });

                    window.location.href = "http://localhost:3000/dev/login/cognito?username=" + email + "&nickname=" + userNickname + "&provider=Kakao";
                }
            </script>
        </body>
    </html>
    """
    return {
        "statusCode": 200,
        "body": nickname_html,
        "headers": {"Content-Type": "text/html"}
    }


def google_login(event, context):
    # How to get user's google account? => Get token from code and decode the token
    code = event['queryStringParameters']['code']
    
    return {
        'statusCode': 200,
        'body': code
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
    is_newbie = cognito.sign_in(email, "Kakao")
    cognito_auth = cognito.get_token(email)
    access_token = cognito_auth['AccessToken']

    return {
        'statusCode': 302,
        'headers': {'Location': 'http://localhost:3000/dev/login/process?email=%s&newbie=%d&token=%s' % (email, is_newbie, access_token)}
    }
    

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
