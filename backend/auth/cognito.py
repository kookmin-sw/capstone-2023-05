import boto3
import os


def sign_in(email: str, nickname: str, identity_provider: str=None) -> str:
    """
    Trying to sign-in with kakao account.\n
    If user didn't register in cognito. Do sign-up\n
    :param email: Kakao email
    :param nickname: Kakao nickname
    :return: ID token
    """
    client = boto3.client('cognito-idp', region_name='ap-northeast-2')

    # Checking if user already in cognito user pool or not.
    # If not exist, do sign-up
    response = client.list_users(
        UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID")
    )
    # print("First Response:\n", response['Users'])

    # TODO: I want to change this for statement to try-excpet structure.
    # Then, I have to know how to catch UserExistsException
    for user in response['Users']:
        if nickname == user['Username']:
            print("Already exist!")
            break
    else:
        sign_up(client, email, nickname)
    
    # Do initiate_auth to get access token
    response = client.initiate_auth(
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': nickname,
            'PASSWORD': "Naruhodo5!"
        },
        ClientId=os.getenv("AWS_COGNITO_CLIENT_ID")
    )
    id_token = response['AuthenticationResult']['IdToken']
    # print("Second response:\n", response)

    # Add user to group in cognito user pool
    if identity_provider is not None:
        response = client.admin_add_user_to_group(
            UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID"),
            Username=nickname,
            GroupName=os.getenv("AWS_COGNITO_USER_POOL_ID") + "_" + identity_provider
        )

    return id_token


def sign_up(_client, email: str, nickname: str):
    """
    Trying to sign-up user logged in from Kakao.\n
    :param _client: boto3.client object
    :param email: User's Kakao email
    :param nickname: User's Kakao nickname
    """
    # Create user to cognito user pool
    _ = _client.admin_create_user(
        UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID"),
        Username=nickname,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': email
            },
            {
                'Name': 'nickname',
                'Value': nickname
            }
        ],
        ValidationData=[
            {
                'Name': 'email',
                'Value': email
            }
        ],
        TemporaryPassword="testPW1234!"
    )

    # Change to new password
    _ = _client.admin_set_user_password(
        UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID"),
        Username=nickname,
        Password='Naruhodo5!',
        Permanent=True
    )


def get_temp_cred(id_token: str, identity_provider: str) -> dict:
    """
    Trying to get temporary credentials to user in cognito user pool.\n
    :param id_token: ID Token you get from cognito user pool\n
    :return: Information about temporary credentials.\n
    """

    # Get Identity ID to get temp credentials.
    client = boto3.client('cognito-identity')
    identity_id = client.get_id(IdentityPoolId=os.getenv('AWS_COGNITO_IDENTITY_POOL_ID'))['IdentityId']
    # print(identity_id)

    # Get temp credentials
    if identity_provider == "Kakao":
        user_pool_id = os.getenv("AWS_COGNITO_USER_POOL_ID")
        response = client.get_credentials_for_identity(
            IdentityId=identity_id,
            Logins={f"cognito-idp.ap-northeast-2.amazonaws.com/{user_pool_id}": id_token}
        )
    elif identity_provider == "Google":
        response = client.get_credentials_for_identity(
            IdentityId=identity_id,
            Logins={f"accouts.google.com": id_token}
        )
    # print(response['Credentials'])

    return response['Credentials']
