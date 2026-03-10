import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture()
def client():
    app_module.reset_activities()

    with TestClient(app_module.app) as test_client:
        yield test_client

    app_module.reset_activities()