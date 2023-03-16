import boto3
import os


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


def sign_in(email: str, identity_provider: str=None) -> tuple[dict, str, bool]:
    """
    Trying to sign-in with kakao account.\n
    If user didn't register in cognito. Do sign-up\n
    :param email: Kakao email
    :return: Authentication information from cognito, nickname and flag for checking newbie
    """
    idp_client = boto3.client('cognito-idp', region_name='ap-northeast-2')

    # Checking if user already in cognito user pool or not.
    # If not exist, do sign-up
    response = idp_client.list_users(
        UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID")
    )

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
    auth_info = response['AuthenticationResult']

    # Add user to group in cognito user pool
    if identity_provider is not None:
        response = idp_client.admin_add_user_to_group(
            UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID"),
            Username=email,
            GroupName=os.getenv("AWS_COGNITO_USER_POOL_ID") + "_" + identity_provider
        )

    return auth_info, nickname, new_created


def sign_up(_client, email: str):
    """
    Trying to sign-up user logged in from Kakao.\n
    :param _client: boto3.client object
    :param email: User's Kakao email
    :param nickname: User's Kakao nickname
    """
    # Create user to cognito user pool
    _client.admin_create_user(
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
    _client.admin_set_user_password(
        UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID"),
        Username=email,
        Password='Naruhodo5!',
        Permanent=True
    )


def delete_account(name: str):
    idp_client = boto3.client('cognito-idp', region_name='ap-northeast-2')
    idp_client.admin_delete_user(
        UserPoolId=os.getenv("AWS_COGNITO_USER_POOL_ID"),
        Username=name
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


def block_token(token: str):
    """
    Revoke a refresh token issued by cognito.\n
    When refresh token is revoked, all access tokens that were previously issued by that refresh token become invalid.\n
    :param token: Refresh token
    """
    idp_client = boto3.client('cognito-idp', region_name='ap-northeast-2')
    idp_client.revoke_token(
        Token=token,
        ClientId=os.getenv("AWS_COGNITO_CLIENT_ID")
    )


if __name__ == "__main__":
    block_token("eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.X23c_HHcrJd5u-Tt8mrhl8xlLwnXOJ_TYRn8L6-ffFsswlRaU-iJ0kRLoTvxU_nZSaFjtyNyOzDxIqmfTUxvBmgbznYJarYqokoasGyT9woULB4pQcuZ1mV1EcJllzxOSj1PZTj-mW7jSB-lkOKAqufZIKt64czPxJ2gLu5M5C_a2OGQIHvNA04hDxa9CieGS6yoRYdGSJmsWlHqMeoVOrOw2r_acCLyiY0RELLjgx_W_Bto_d5Pv6fkccrgBFaIeoVP_6MTNqUd2WqPX_PyLYVcFb3SMEWZx5pZEaWJ9SK-zk4RR1pm-GoeYieu5wCCqeNdGUCMCyqq_GTQTUGlMA.yIFxJAhqxTntkBKk._8qdt_ACK5uA4J9mABqLtR2LaCDSa-WXXJ7dYTb0jjHD_zZbFnrGfYxkhh-3Isvg7_AC6uON-Tsh7LrnMjAAiePZH8Z88ae6xiIoyCe13GnPuH6dXtM3HIiuc1-2XQy0kzIwimxBpfQGEKlqltZiBRoPlVmcLY6P1xyHPVNPgnwI_2Zgf2ntuLskQnYeK-qzQUBX1TSQ3qYQgKQQLnr4iqmZRJ-R4ctraG67S5vYOjIJCMbFOWTL2YT8OG-pvcWtCn59mUAyvpssFTmMz6YaDhZRcplg8ahefkLya79RsLkxpI3AgSsdlf2Y6wptYkHWrdZUDzj54kGgTewW9U_fw8C--AWa1Qpgq60Rm2v6tIDYBzJOGH1BoKyC3H6wFPhglO9Xz97awgXcnPUzBsJ5MVXS7GrRJxhWIU9IdGHqkA81aeDek4TXmBcmO2KXvsC5friVoI3Ae9v7zU1bzOfQeWf8aNr0WDwe-hXd5VphfBwT60vSmZmcIk4UG4i95lLp8kMoEVR4uWYdpCo0g6vcgn3ASI9ToukFYlXK2Lb8M9XTTuKziWMRdNr5XuOulsbm1aNRj5Aui7yPg4HglRLWWOJo377mVOXF4Yz1GeSUWKJLuKjf22g-TbKw5hMqt4f1QWwKEhzFFc8c_ZWdQsSqj4y0S0mxMu2x_vQOOIV9IxLA43wDIdl3VPnal2h3YrNYMbxbPeoAFjs4yVaaYBvUo8Y1HhLSXCSAjpc2ueejxYP8PsXcQH3Ton5mVz5Oc7fND_D60il-tq4FiBm7NzG3IDIRYrlx2kdjSAiMTHtpbv_4lxXY8VuyG-brjHPqTXn_tiEy2C8TsCtFeEYmVIlFNlotfyFnIy0WaR8P0trEZif9g_FNvsBIKsmFvvhdDqLyOIrvRMqj75S-ssl4nfR8zjHQGJ0Ft3KIe4w4kRQ-Ug0Jp3JcJYO8kKz0JmKeOqIxyhQF--HzGaVgxf4qI_MLW_Qy4oxf9bHfeWxkg1SPlhew-xdAhNgOG5gLq_rGVk9Y7kyw3yo9iJdYFL5tcberlJF-uL1hRf5x4_U8Zm-YcfAyDdb2rq-V1SGKmQD9esv7fUG9OvfxLKmLhOpHhG7DGpyo-kwHM-LDKTQgnnyGenG9eIbnis3IuUICKaQEkcTFseAxW5quQJoDBaQ7d-JzQnyTxPHHqG6DoFqYDhlOmK1ojudtoFln5eUBPPPCSWwSqlRRR_6og9Yg1P4GixWMfIv0WCFTFMeUQJBGKfXAwK1WU3GRFjGFp5v8pFMh17vsg412qclD98etX-rgijYkVHaDou10U8bvAvH5E-SEcEDAwL5tvXlPQOav.uDbHmlSbau3HO_STn07_EQ")
    