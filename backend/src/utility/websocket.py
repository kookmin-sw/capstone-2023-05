import functools
import json
import os

import boto3


class WebSocketClient:
    def __init__(self, api_endpoint):
        self._api_endpoint = api_endpoint
        self._client = boto3.client('apigatewaymanagementapi', endpoint_url=self._api_endpoint)

    def send(self, connection_id, data):
        try:
            self._client.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps(data).encode('utf-8')
            )
        except:
            print(f"Failed to send message to connection {connection_id}")

    def broadcast(self, connection_ids, payload):
        for connection_id in connection_ids:
            self.send(connection_id, payload)
    


def wsclient(func):
    functools.wraps(func)
    def wrapper(event, context):
        if os.environ.get('IS_OFFLINE') == 'true':
            ws_endpoint = "http://localhost:3001"
        else:
            ws_endpoint = f"https://{event['requestContext']['domainName']}/{event['requestContext']['stage']}"

        wsclient = WebSocketClient(ws_endpoint)
        return func(event, context, wsclient)

    return wrapper