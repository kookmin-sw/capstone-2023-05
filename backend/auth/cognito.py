import boto3
import os
import json


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


def block_token(token: str) -> dict:
    """
    Revoke a refresh token issued by cognito.\n
    When refresh token is revoked, all access tokens that were previously issued by this refresh token become invalid.\n
    :param token: Refresh token
    """
    response = idp_client = boto3.client('cognito-idp', region_name='ap-northeast-2')
    # Revoke access token
    idp_client.revoke_token(
        Token=token,
        ClientId=os.getenv("AWS_COGNITO_CLIENT_ID")
    )

    # Expiring session token
    

    return response


if __name__ == "__main__":
    response = block_token("eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.OgCcdYkTwDxIgSjBiyN4YUSp-ycGHEunT4VUhfYCP6nf86jW_7pGAwgPhhE1rT5mxfzzN06PJ2fXns3Qsf5Zy2RN0SVMdXyNZpLosJKFkmhvZmsM3fLvbZsoSoILgCxgLQdd6adoIyQ_VOjO0Ga2LfajJH35aw3aheLrBZTMx9tZByZEuAuleI499bZIzS7-2ZOmZdRvG5Yjiu1jAZaWIuoOSutSKgNK6e238n1hz-aiwQTPXwfLsAuu0j9D4ZPMvEaHDnTm_Hj4H-Duzu0c3OYR8SLIfCnxBJj49W5U-Qd7mW03QEtau-FYLxmDwUtAIlBVwTm5oO02-Ta1l-4wFg.OQkhJN8K0f63gWON.6xIn60jBNMXgALKrPwI9B29yC83Wi4S3iiuuVlATbFhJl7CIQmPVlFZOesKkVVK6iarEHeAkS8iMurSENU1Al9qRsZfXGc31iNjNWUGHBmg1ut-vAcjz20_VrCkCK3-P7eFfz7L4mNtfiVWLorQ7uK0aYKSujw4O6ONSSHc0PpbuVRoJsfFSwbzjtyfZEEmkK7jOIN8Jad6s508LWhcr-GSVDqYZIIX-10RDIQAyemHLVkbRtmUCaqBovGpY32y7czKRhixACcJ2izQZ5vdc-FgiYBP_P9mhERZhyh6XjTM8jxBYKvHmjNYev9M5OHULQWSaMdI7eQ-FJ7SX8rjIrdhmwtw-ZxcSMVej_AMDKLFcWCGi1kKIl7TNbBEE5mD482NTj9LhKlPkxc1HvVisIwSIiOg3rDQskw_s9OPY44qXuX4w6GeCK1hOjxE08clPWyUbT1w0-WgQyR0YBOJgAT3THFh87x-dLz7DfYVbUuyT7inOSUBC5PUNeDyvrx-108Zu3BGFOWcYcMRjxsmX-LGw_rKNRJLSvYUchnq0AgJFz7bjI_yXZKy0OVx02RZj3P3FL89XuRPm09fTS87aUmncH-oF4eyAYaR0M922fnvylzvFlKauOYJFDJqWqisjd1pi39T1YJA_cdku06nzgbc4ZIWS1dyIzk5mZqcqCnH4wD9axPYSmnOQQIjV5WcGkeTvQApNxfhi9T4lbOnaTfdPnolW9kAMglv7OZEzxd2NPR_F941uaZJznrdB0WEvZEQQazoyf2yoLGhhj8zNCBPC9WdR5geQsIMmIlDbR2MMfjYbtvTfoC4m7JP3EfEPOrrB5jIB7Q2J7XuDmQCifB3OVV17KjsyC68OifXK-AQiGrcz9mQcsfDzVYZYJ2Btvpj8FVbJd6CQM-Hw2gzQQ0iyz-Hg3zkaLDOjz9w7CZ-GJjUan6uKyzLVpqsyJNrJBH4yQbx12h5du1WaCz1WjP1hSslkkzjpF1OV4ZMFv3W-fh2VGRM3m4NtTymbLwTDKvsLD76x2hhSDX8Z8NbSfXXX5y6EL5b8FHBcpDC3UTYZzbahv1oi8luWPSh6FWie1A9dYJc_Ro-n1EJf9IbfUuRqtKX6Gdk2uqcnO1bJ3bo9bwNmUkgmkBiOs6KIia0Vzvy5uSJVktvIbiFtnm4Yv35t7vaBkcBOYZWKxoUZodK64s7ELX1jJ5eiTvnCoKucdEGqrj4OM8amLCKtyWayj68koKlCbop7Welljs3xoThUV6LPWzAQDWnb1Gwa3UrMj6bSfSRVTZa3rlnl1DYVknTH-_sdVhDAMyCBX7bj8CkOcnauRDNedDa4.TuOykOaFSJW49y1yVcPxxg")
    
    