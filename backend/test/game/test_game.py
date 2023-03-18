import json
import pytest

from src.game import app


def test_hello_world():
    msg = app.hello()
    assert msg == "Hello World!"

