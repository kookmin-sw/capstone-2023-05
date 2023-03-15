from src.game import app


def hello(event, context):
    return app.hello(event)


def create_room(event, context):
    # get post data from event
    pass