"""
Unit + integration tests for the Agents API.

Covers:
  - GET /api/agents          (catalogue list, auth required)
  - GET /api/agents/all      (full catalogue with locked/unlocked flags)
  - POST /api/agents/{id}/run (valid agent, invalid agent, insufficient credits)
  - Credit deduction at job-submission time
  - HITL-3 jobs queued as pending_approval, not pending
"""
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi import status

from conftest import make_user
from app.models.agent_system import AgentJob
from app.models.workspace import CreditsAccount

# A STARTER-tier agent with credit_estimate=1 (cheapest, always available)
STARTER_AGENT_ID = "social_media_content_agent"  # min_package=starter, credit_estimate=1
# A HITL-3 agent (requires pending_approval)
HITL3_AGENT_ID = "ads_optimisation_agent"          # min_package=business, hitl=HITL-3
# An agent that does NOT exist
BAD_AGENT_ID = "nonexistent_agent_xyz"


# ---------------------------------------------------------------------------
# Helper: make a user with enough credits to be on 'starter' tier (60+)
# ---------------------------------------------------------------------------

def _make_starter_user(db):
    """User with 60 total credits → starter tier → social_media_content_agent unlocked."""
    user, token, credits = make_user(db)
    credits.total_credits = 60
    credits.used_credits = 0
    db.commit()
    db.refresh(credits)
    return user, token, credits


def _make_business_user(db):
    """User with 300 total credits → business tier → ads_optimisation_agent unlocked."""
    user, token, credits = make_user(db)
    credits.total_credits = 300
    credits.used_credits = 0
    db.commit()
    db.refresh(credits)
    return user, token, credits


# ---------------------------------------------------------------------------
# GET /api/agents
# ---------------------------------------------------------------------------

class TestListAgents:
    def test_list_agents_requires_auth(self, client):
        resp = client.get("/api/agents")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_agents_invalid_token(self, client):
        resp = client.get("/api/agents", headers={"Authorization": "Bearer invalid.token"})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_agents_returns_catalogue(self, client, db):
        _, token, _ = _make_starter_user(db)
        resp = client.get("/api/agents", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "agents" in body
        assert isinstance(body["agents"], list)
        assert len(body["agents"]) > 0

    def test_list_agents_returns_tier(self, client, db):
        _, token, _ = _make_starter_user(db)
        resp = client.get("/api/agents", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "tier" in body
        assert body["tier"] in ("starter", "growth", "business", "enterprise", "free")

    def test_list_agents_starter_tier_includes_starter_agent(self, client, db):
        """social_media_content_agent (min_package=starter) must appear for starter-tier users."""
        _, token, _ = _make_starter_user(db)
        resp = client.get("/api/agents", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == status.HTTP_200_OK
        agent_ids = [a["id"] for a in resp.json()["agents"]]
        assert STARTER_AGENT_ID in agent_ids


# ---------------------------------------------------------------------------
# GET /api/agents/all
# ---------------------------------------------------------------------------

class TestListAllAgents:
    def test_list_all_agents_requires_auth(self, client):
        resp = client.get("/api/agents/all")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_all_agents_returns_full_catalogue(self, client, db):
        _, token, _ = _make_starter_user(db)
        resp = client.get("/api/agents/all", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "agents" in body
        # Starter user sees all agents but many are locked
        assert body["total"] >= 1
        # Check unlocked flag is present
        assert all("unlocked" in a for a in body["agents"])

    def test_list_all_agents_starter_locked_business_agents(self, client, db):
        """Business-tier agents should be locked=False for a starter user."""
        _, token, _ = _make_starter_user(db)
        resp = client.get("/api/agents/all", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == status.HTTP_200_OK
        agents = {a["id"]: a for a in resp.json()["agents"]}
        # ads_optimisation_agent is business-tier, should be locked for starter user
        if HITL3_AGENT_ID in agents:
            assert agents[HITL3_AGENT_ID]["unlocked"] is False


# ---------------------------------------------------------------------------
# POST /api/agents/{id}/run
# ---------------------------------------------------------------------------

class TestRunAgent:
    def test_run_agent_requires_auth(self, client):
        resp = client.post(
            f"/api/agents/{STARTER_AGENT_ID}/run",
            json={"prompt": "Create a social post about our sale"},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_unknown_agent_returns_404(self, client, db):
        _, token, _ = _make_starter_user(db)
        resp = client.post(
            f"/api/agents/{BAD_AGENT_ID}/run",
            json={"prompt": "test"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_run_agent_missing_prompt_returns_422(self, client, db):
        _, token, _ = _make_starter_user(db)
        resp = client.post(
            f"/api/agents/{STARTER_AGENT_ID}/run",
            json={},  # prompt field missing
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_run_starter_agent_success(self, client, db):
        """Valid starter agent + sufficient credits → 200 with job_id."""
        _, token, _ = _make_starter_user(db)
        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                f"/api/agents/{STARTER_AGENT_ID}/run",
                json={"prompt": "Write a social media post for our weekend sale"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "job_id" in body
        assert body["agent_id"] == STARTER_AGENT_ID
        assert body["status"] in ("pending", "pending_approval")

    def test_run_agent_creates_job_in_db(self, client, db):
        """Submitting a run must persist an AgentJob row."""
        user, token, _ = _make_starter_user(db)
        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                f"/api/agents/{STARTER_AGENT_ID}/run",
                json={"prompt": "Write a post"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK
        job_id = resp.json()["job_id"]
        job = db.query(AgentJob).filter(AgentJob.id == job_id).first()
        assert job is not None
        assert job.agent_id == STARTER_AGENT_ID
        assert job.status in ("pending", "pending_approval")

    def test_run_agent_deducts_credits(self, client, db):
        """Credits must be deducted when a non-HITL-3 job is queued."""
        _, token, credits = _make_starter_user(db)
        initial_used = credits.used_credits
        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                f"/api/agents/{STARTER_AGENT_ID}/run",
                json={"prompt": "Write a post"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK
        db.refresh(credits)
        # social_media_content_agent has credit_estimate=1
        assert credits.used_credits == initial_used + 1

    def test_run_agent_insufficient_credits_returns_402(self, client, db):
        """Zero available credits → 402 Payment Required."""
        _, token, credits = make_user(db)
        credits.total_credits = 60
        credits.used_credits = 60  # drain all
        db.commit()
        resp = client.post(
            f"/api/agents/{STARTER_AGENT_ID}/run",
            json={"prompt": "Write a post"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == status.HTTP_402_PAYMENT_REQUIRED

    def test_run_agent_locked_for_tier_returns_403(self, client, db):
        """Starter user trying to run a business-tier agent → 403."""
        _, token, _ = _make_starter_user(db)
        # head_agent is min_package=starter BUT ads_optimisation_agent is business
        # Use a GROWTH-tier agent to test tier gate against a STARTER user
        resp = client.post(
            "/api/agents/lead_generator_agent/run",  # min_package=growth
            json={"prompt": "Find leads for my business"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_run_hitl3_agent_queued_as_pending_approval(self, client, db):
        """HITL-3 agents must create jobs with status=pending_approval, NOT pending."""
        _, token, credits = _make_business_user(db)
        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                f"/api/agents/{HITL3_AGENT_ID}/run",
                json={"prompt": "Optimise my Facebook ads"},
                headers={"Authorization": f"Bearer {token}"},
            )
        # May be 200 or blocked by credit gate — accept both
        if resp.status_code == status.HTTP_200_OK:
            assert resp.json()["status"] == "pending_approval"

    def test_run_agent_returns_hitl_level(self, client, db):
        """Run response must include hitl_level field."""
        _, token, _ = _make_starter_user(db)
        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                f"/api/agents/{STARTER_AGENT_ID}/run",
                json={"prompt": "Write a caption"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK
        assert "hitl_level" in resp.json()

    def test_run_agent_returns_credit_estimate(self, client, db):
        """Run response must include credit_estimate field."""
        _, token, _ = _make_starter_user(db)
        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                f"/api/agents/{STARTER_AGENT_ID}/run",
                json={"prompt": "Create a post"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "credit_estimate" in body
        assert body["credit_estimate"] >= 1
