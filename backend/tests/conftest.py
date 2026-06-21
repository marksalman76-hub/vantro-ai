import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_user_data():
    return {
        "email": "test@example.com",
        "password": "Test123!",
        "name": "Test User",
    }

@pytest.fixture
def test_user(client, test_user_data):
    client.post("/api/auth/register", json=test_user_data)
    return test_user_data

@pytest.fixture
def authenticated_client(client, test_user_data):
    client.post("/api/auth/register", json=test_user_data)
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {token}"
    return client