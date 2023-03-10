import requests
import os


def get_email(code):
    """
    Trying to login through Kakao account\n
    You should replace those things below\n
    - Kakao application: client_id(REST API Key), client_secret, redirect_uri\n
    :return:
    """

    client_id = os.getenv("KAKAO_REST_API_KEY")
    client_secret = os.getenv("KAKAO_CLIENT_SECRET")
    # TODO: Change redirect_uri to env variable
    redirect_uri = f'http://localhost:3000/dev/login/kakao'

    parameters = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': code
    }
    response = requests.post("https://kauth.kakao.com/oauth/token", params=parameters)
    access_token = response.json()['access_token']

    headers = {'Authorization': f'Bearer {access_token}'}
    user_information = requests.get("https://kapi.kakao.com/v2/user/me", headers=headers).json()
    # print(user_information)

    user_email = user_information['kakao_account']['email']

    return user_email