import boto3
import os


def set_nickname(user_name: str, nickname: str):
    idp_client = boto3.client('cognito-idp', region_name='ap-northeast-2')
    _ = idp_client.admin_update_user_attributes(
        UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID"),
        Username=user_name,
        UserAttributes=[
            {
                'Name': 'nickname',
                'Value': nickname
            }
        ]
    )


def sign_in(email: str, identity_provider: str=None) -> tuple[str, bool]:
    """
    Trying to sign-in with kakao account.\n
    If user didn't register in cognito. Do sign-up\n
    :param email: Kakao email
    :param nickname: Kakao nickname
    :return: ID token and flag for checking newbie
    """
    idp_client = boto3.client('cognito-idp', region_name='ap-northeast-2')

    # Checking if user already in cognito user pool or not.
    # If not exist, do sign-up
    response = idp_client.list_users(
        UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID")
    )
    # print("First Response:\n", response['Users'])

    # TODO: I want to change this for statement to try-excpet structure.
    # Then, I have to know how to catch UserExistsException
    new_created = False
    nickname = "TempNickname"
    for user in response['Users']:
        if email == user['Username']:
            for attr in user['Attributes']:
                if attr['Name'] == "nickname":
                    nickname = attr['Value']
                    break
            break
    else:
        sign_up(idp_client, email)
        new_created = True
    
    # Do initiate_auth to get access token
    response = idp_client.initiate_auth(
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': email,
            'PASSWORD': "Naruhodo5!"
        },
        ClientId=os.getenv("AWS_COGNITO_CLIENT_ID")
    )
    id_token = response['AuthenticationResult']['IdToken']
    # print("Second response:\n", response)

    # Add user to group in cognito user pool
    if identity_provider is not None:
        response = idp_client.admin_add_user_to_group(
            UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID"),
            Username=email,
            GroupName=os.getenv("AWS_COGNITO_USER_POOL_ID") + "_" + identity_provider
        )

    return id_token, nickname, new_created


def sign_up(_client, email: str):
    """
    Trying to sign-up user logged in from Kakao.\n
    :param _client: boto3.client object
    :param email: User's Kakao email
    :param nickname: User's Kakao nickname
    """
    # Create user to cognito user pool
    _ = _client.admin_create_user(
        UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID"),
        Username=email,
        UserAttributes=[
            {
                'Name': 'nickname',
                'Value': 'TempNickname'
            }
        ],
        TemporaryPassword="testPW1234!"
    )

    # Change to new password
    _ = _client.admin_set_user_password(
        UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID"),
        Username=email,
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
    idp_client = boto3.client('cognito-identity')
    identity_id = idp_client.get_id(IdentityPoolId=os.getenv('AWS_COGNITO_IDENTITY_POOL_ID'))['IdentityId']
    # print(identity_id)

    # Get temp credentials
    if identity_provider == "Kakao":
        user_pool_id = os.getenv("AWS_COGNITO_USER_POOL_ID")
        response = idp_client.get_credentials_for_identity(
            IdentityId=identity_id,
            Logins={f"cognito-idp.ap-northeast-2.amazonaws.com/{user_pool_id}": id_token}
        )
    elif identity_provider == "Google":
        response = idp_client.get_credentials_for_identity(
            IdentityId=identity_id,
            Logins={f"accouts.google.com": id_token}
        )
    # print(response['Credentials'])

    return response['Credentials']
