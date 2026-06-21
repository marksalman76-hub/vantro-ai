import pytest
from fastapi import status


@pytest.mark.unit
class TestRegistration:
    def test_register_success(self, client, test_user_data):
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert "access_token" in body
        assert "user_id" in body

    def test_register_duplicate_email(self, client, registered_user, test_user_data):
        response = client.post(
            "/api/auth/register",
            json={"email": registered_user["email"], "password": "Diff123!", "name": "Diff"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_fields(self, client):
        response = client.post("/api/auth/register", json={"email": "x@x.com"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.unit
class TestLogin:
    def test_login_success(self, client, registered_user, test_user_data):
        response = client.post(
            "/api/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()

    def test_login_wrong_password(self, client, registered_user, test_user_data):
        response = client.post(
            "/api/auth/login",
            json={"email": test_user_data["email"], "password": "Wrong123!"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_unknown_email(self, client):
        response = client.post(
            "/api/auth/login",
            json={"email": "nobody@example.com", "password": "Test123!"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout(self, client):
        response = client.post("/api/auth/logout")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.unit
class TestProtectedEndpoints:
    def test_get_current_user_no_token(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_invalid_token(self, client):
        response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_valid_token(self, authenticated_client):
        response = authenticated_client.get("/api/auth/me")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert "email" in body
        assert "id" in body
