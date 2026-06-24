"""Integration tests for agent job lifecycle."""
import pytest
from fastapi import status


@pytest.mark.unit
class TestAgentJobList:
    def test_list_jobs_unauthenticated(self, client):
        resp = client.get("/api/agents/jobs")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_jobs_authenticated_empty(self, client, authenticated_client):
        resp = authenticated_client.get("/api/agents/jobs")
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "total" in body
        assert "jobs" in body
        assert isinstance(body["jobs"], list)

    def test_list_jobs_pagination_params(self, client, authenticated_client):
        resp = authenticated_client.get("/api/agents/jobs?skip=0&limit=5")
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert body["skip"] == 0
        assert body["limit"] == 5

    def test_list_jobs_invalid_limit(self, client, authenticated_client):
        resp = authenticated_client.get("/api/agents/jobs?limit=999")
        # FastAPI Query validation: limit capped at 100
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY)
        if resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            body = resp.json()
            assert "detail" in body


@pytest.mark.unit
class TestAgentRun:
    def test_run_agent_unauthenticated(self, client):
        resp = client.post("/api/agents/content_writer/run", json={"prompt": "Write a headline"})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_unknown_agent(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/nonexistent_agent_xyz/run",
            json={"prompt": "test"},
        )
        assert resp.status_code in (
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_run_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post("/api/agents/content_writer/run", json={})
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )
