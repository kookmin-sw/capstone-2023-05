import boto3


def get_temp_cred(user_name: str):
    sts_client = boto3.client('sts', region_name='ap-northeast-2')
    response = sts_client.get_federation_token(
        Name=user_name
    )

    return response['Credentials']