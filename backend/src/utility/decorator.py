import functools


def cors(func):
    @functools.wraps(func)
    def wrapper(event, context):
        response = func(event, context)
        if 'headers' not in response:
            response['headers'] = {}
        response['headers']['Access-Control-Allow-Origin'] = '*'
        response['headers']['Access-Control-Allow-Credentials'] = True
        return response
    return wrapper