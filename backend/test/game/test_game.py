import json
import pytest

from src.game import app


def test_hello_world():
    resp = app.hello({'hello': 'world'})
    assert resp['statusCode'] == 200

    body = json.loads(resp['body'])
    assert body['event']['hello'] == 'world'