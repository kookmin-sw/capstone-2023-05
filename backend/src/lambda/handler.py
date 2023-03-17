from src.game import app


def hello(event, context):
    return app.hello(event)


def hello_redis(event, context):
    return app.hello_redis()


def hello_db(event, context):
    return app.hello_db()