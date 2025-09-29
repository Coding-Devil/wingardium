#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ai.routes.v1.health import router

app = FastAPI()
app.include_router(router)


@pytest.fixture
def client():
    return TestClient(app)


def test_ok_health(client):
    response = client.get("/health")
    assert response.status_code == 200  # Check if endpoint is reachable
    data = response.json()
    assert data["status"] == "ok"
