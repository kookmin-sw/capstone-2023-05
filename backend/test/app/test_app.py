import pytest
import src.app.handler as handler


def test_hello_world():
    resp = handler.hello({}, {})
    assert resp["statusCode"] == 200