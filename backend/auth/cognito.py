import boto3
import os


def get_username(email: str) -> str:
    idp_client = boto3.client('cognito-idp', region_name='ap-northeast-2')
    response = idp_client.list_users(
        UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID")
    )

    for user in response['Users']:
        if email == user['Username']:
            for attr in user['Attributes']:
                # If user logged in from Kakao, nickname will be exist
                # Else if user logged in from Google, he doesn't have nickname
                # So find from email attribute
                if attr['Name'] == "nickname" or attr['Name'] == "email":
                    return attr['Value']
        

def set_nickname(user_name: str, nickname: str) -> None:
    """
    Trying to setting nickname\n
    :param user_name: Username(This should be same as email)
    :param nickname: A nickname you want to set
    """

    idp_client = boto3.client('cognito-idp', region_name='ap-northeast-2')
    idp_client.admin_update_user_attributes(
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
    :return: nickname and flag for checking newbie
    """

    new_created = False
    cognito_user_name = get_username(email)
    if not cognito_user_name:
        sign_up(email)
        new_created = True

    # Add user to group in cognito user pool
    idp_client = boto3.client('cognito-idp', region_name='ap-northeast-2')
    if identity_provider is not None:
        response = idp_client.admin_add_user_to_group(
            UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID"),
            Username=email,
            GroupName=os.getenv("AWS_COGNITO_USER_POOL_ID") + "_" + identity_provider
        )

    return cognito_user_name, new_created


def sign_up(email: str):
    """
    Trying to sign-up user logged in from Kakao.\n
    :param email: User's Kakao email
    :param nickname: User's Kakao nickname
    """

    client = boto3.client('cognito-idp', region_name='ap-northeast-2')
    # Create user to cognito user pool
    client.admin_create_user(
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
    client.admin_set_user_password(
        UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID"),
        Username=email,
        Password='Naruhodo5!',
        Permanent=True
    )


def sign_out(access_token: str):
    """
    Trying to sign-out via cognito.\n
    :param access_token: Access token you got from aws cognito\n
    """

    idp_client = boto3.client('cognito-idp', region_name='ap-northeast-2')
    idp_client.global_sign_out(AccessToken=access_token)


def delete_account(name: str):
    """
    Trying to delete user in cognito user pool.\n
    :param name: The email you registered.
    """

    idp_client = boto3.client('cognito-idp', region_name='ap-northeast-2')
    idp_client.admin_delete_user(
        UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID"),
        Username=name
    )


def get_token(user_name: str) -> dict:
    """
    Trying to get tokens(Access Token, Refresh Token, ID Token).\n
    :param email: User's email
    :return: Result for authentication
    """

    idp_client = boto3.client('cognito-idp')
    # Do initiate_auth to get access token
    response = idp_client.initiate_auth(
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': user_name,
            'PASSWORD': "Naruhodo5!"
        },
        ClientId=os.getenv("AWS_COGNITO_CLIENT_ID")
    )

    return response['AuthenticationResult']


def get_temp_cred(id_token: str, user_name=None) -> dict:
    """
    Trying to get temporary credentials to user in cognito user pool.\n
    :param id_token: ID Token you get from cognito user pool\n
    :param identity_provider: Kakao or Google\n
    :param user_name: It is required if identity_provider is Google\n
    :return: Information about temporary credentials.\n
    """

    # Get Identity ID to get temp credentials.
    idp_client = boto3.client('cognito-identity')
    identity_id = idp_client.get_id(IdentityPoolId=os.getenv('AWS_COGNITO_IDENTITY_POOL_ID'))['IdentityId']

    # Get temp credentials
    user_pool_id = os.getenv("AWS_COGNITO_USER_POOL_ID")
    response = idp_client.get_credentials_for_identity(
        IdentityId=identity_id,
        Logins={f"cognito-idp.ap-northeast-2.amazonaws.com/{user_pool_id}": id_token}
    )      

    return response['Credentials']
