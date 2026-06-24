"""Integration tests for HITL approval flow."""
import os
import pytest
from fastapi import status


ADMIN_EMAIL = "admin@vantro.ai"


@pytest.fixture
def admin_token(client):
    """Register and get token for an admin-email user."""
    os.environ["ADMIN_EMAIL"] = ADMIN_EMAIL
    client.post("/api/auth/register", json={
        "email": ADMIN_EMAIL, "password": "Admin123!", "name": "Admin",
    })
    resp = client.post("/api/auth/login", json={
        "email": ADMIN_EMAIL, "password": "Admin123!",
    })
    return resp.json().get("access_token", "")


@pytest.mark.unit
class TestAdminAgentJobs:
    def test_list_agent_jobs_unauthenticated(self, client):
        resp = client.get("/api/admin/agents/jobs")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_agent_jobs_non_admin(self, client, authenticated_client):
        resp = authenticated_client.get("/api/admin/agents/jobs")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_list_agent_jobs_admin(self, client, admin_token):
        resp = client.get(
            "/api/admin/agents/jobs",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "jobs" in body
        assert "total" in body

    def test_list_agent_jobs_status_filter(self, client, admin_token):
        resp = client.get(
            "/api/admin/agents/jobs?status=pending_approval",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        for job in body["jobs"]:
            assert job["status"] == "pending_approval"

    def test_approve_nonexistent_job(self, client, admin_token):
        resp = client.post(
            "/api/admin/agents/jobs/nonexistent-job-id/approve",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_reject_nonexistent_job(self, client, admin_token):
        resp = client.post(
            "/api/admin/agents/jobs/nonexistent-job-id/reject",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.unit
class TestAdminPagination:
    def test_admin_jobs_pagination(self, client, admin_token):
        resp = client.get(
            "/api/admin/agents/jobs?skip=0&limit=10",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert body["skip"] == 0
        assert body["limit"] == 10

    def test_admin_users_pagination(self, client, admin_token):
        resp = client.get(
            "/api/admin/users?skip=0&limit=5",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "users" in body
        assert body["limit"] == 5
