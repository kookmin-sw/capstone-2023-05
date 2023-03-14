import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "database: this test has database access.")
