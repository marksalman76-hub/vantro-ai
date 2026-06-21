import pytest
from fastapi import status

@pytest.mark.unit
class TestRegistration:
    def test_register_success(self, client, test_user_data):
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_register_duplicate_email(self, client, test_user, test_user_data):
        response = client.post(
            "/api/auth/register",
            json={"email": test_user["email"], "password": "Diff123!", "name": "Diff"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.unit
class TestLogin:
    def test_login_success(self, client, test_user_data):
        client.post("/api/auth/register", json=test_user_data)
        response = client.post("/api/auth/login", json={"email": test_user_data["email"], "password": test_user_data["password"]})
        assert response.status_code == status.HTTP_200_OK
    
    def test_login_wrong_password(self, client, test_user, test_user_data):
        response = client.post("/api/auth/login", json={"email": test_user_data["email"], "password": "Wrong123!"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.unit
class TestProtectedEndpoints:
    def test_get_current_user_no_token(self, client):
        response = client.get("/api/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED