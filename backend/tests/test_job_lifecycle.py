"""
Integration tests: full job lifecycle.

Flow under test:
  make_user(db) → POST /api/agents/{id}/run → job row in DB → credits deducted

The LLM executor (agent_executor.execute_agent) is NOT called in these tests —
the worker is disabled by TESTING=1, so jobs remain in 'pending' status.
We verify DB state directly using the `db` fixture.

The auth register/login endpoints are also tested separately in test_auth.py;
here we focus on what happens AFTER authentication.
"""
import uuid
from unittest.mock import patch

import pytest
from fastapi import status

from conftest import make_user
from app.models.agent_system import AgentJob
from app.models.workspace import CreditsAccount

STARTER_AGENT = "social_media_content_agent"   # min_package=starter, credit_estimate=1
HITL1_AGENT   = "intake_trial_agent"           # min_package=starter, hitl=HITL-1
HITL3_AGENT   = "ads_optimisation_agent"       # min_package=business, hitl=HITL-3, credit=4


def _with_starter_credits(db, user, credits):
    """Set credits to starter tier (60 total, 0 used)."""
    credits.total_credits = 60
    credits.used_credits = 0
    db.commit()
    db.refresh(credits)
    return credits


def _with_business_credits(db, user, credits):
    """Set credits to business tier (300 total, 0 used)."""
    credits.total_credits = 300
    credits.used_credits = 0
    db.commit()
    db.refresh(credits)
    return credits


class TestFullJobLifecycle:
    def test_run_agent_creates_job(self, client, db):
        """Submit a run request → AgentJob row must exist in DB."""
        user, token, credits = make_user(db)
        _with_starter_credits(db, user, credits)

        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                f"/api/agents/{STARTER_AGENT}/run",
                json={"prompt": "Create a post about our product launch"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK, resp.text
        job_id = resp.json()["job_id"]

        job = db.query(AgentJob).filter(AgentJob.id == job_id).first()
        assert job is not None, "AgentJob row must exist after successful run request"
        assert job.agent_id == STARTER_AGENT
        assert job.status in ("pending", "pending_approval")

    def test_job_row_has_correct_workspace_id(self, client, db):
        """Job row must be scoped to the user's workspace."""
        from app.models import Organization
        from app.models.workspace import Workspace
        user, token, credits = make_user(db)
        _with_starter_credits(db, user, credits)

        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                f"/api/agents/{STARTER_AGENT}/run",
                json={"prompt": "Draft a social post"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK
        job_id = resp.json()["job_id"]

        job = db.query(AgentJob).filter(AgentJob.id == job_id).first()
        org = db.query(Organization).filter(Organization.owner_id == user.id).first()
        ws = db.query(Workspace).filter(Workspace.organization_id == org.id).first()
        assert job.workspace_id == ws.id

    def test_credit_deduction_after_run(self, client, db):
        """Credits must be deducted (used_credits incremented) after a non-HITL-3 job."""
        user, token, credits = make_user(db)
        _with_starter_credits(db, user, credits)
        initial_used = credits.used_credits

        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                f"/api/agents/{STARTER_AGENT}/run",
                json={"prompt": "Write a caption"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK

        db.refresh(credits)
        credit_cost = resp.json()["credit_estimate"]
        assert credits.used_credits == initial_used + credit_cost

    def test_job_status_is_pending_for_hitl1(self, client, db):
        """HITL-1 jobs (intake_trial_agent) should be queued as 'pending', not pending_approval."""
        user, token, credits = make_user(db)
        _with_starter_credits(db, user, credits)

        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                f"/api/agents/{HITL1_AGENT}/run",
                json={"prompt": "Qualify this lead: interested in our product"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        # HITL-1 should not require approval
        assert body["status"] == "pending"

    def test_hitl3_job_queued_as_approved(self, client, db):
        """HITL-3 agent auto-approved — submitter IS the approval authority."""
        user, token, credits = make_user(db)
        _with_business_credits(db, user, credits)

        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                f"/api/agents/{HITL3_AGENT}/run",
                json={"prompt": "Optimise my Facebook ad campaign budget"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert body["status"] == "approved"

        # Confirm in DB
        job = db.query(AgentJob).filter(AgentJob.id == body["job_id"]).first()
        assert job is not None
        assert job.status == "approved"

    def test_hitl3_credits_deducted_on_auto_approval(self, client, db):
        """HITL-3 jobs auto-approved at submission — credits deducted immediately."""
        user, token, credits = make_user(db)
        _with_business_credits(db, user, credits)
        initial_used = credits.used_credits

        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                f"/api/agents/{HITL3_AGENT}/run",
                json={"prompt": "Launch a Google Ads campaign"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["status"] == "approved"

        db.refresh(credits)
        # Credits ARE pre-committed for auto-approved HITL-3 jobs
        assert credits.used_credits > initial_used

    def test_multiple_jobs_each_deduct_credits(self, client, db):
        """Running the same agent twice deducts credits twice."""
        user, token, credits = make_user(db)
        _with_starter_credits(db, user, credits)

        with patch("app.routes.agents.send_approval_needed"):
            r1 = client.post(
                f"/api/agents/{STARTER_AGENT}/run",
                json={"prompt": "First post"},
                headers={"Authorization": f"Bearer {token}"},
            )
            r2 = client.post(
                f"/api/agents/{STARTER_AGENT}/run",
                json={"prompt": "Second post"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert r1.status_code == status.HTTP_200_OK
        assert r2.status_code == status.HTTP_200_OK

        db.refresh(credits)
        credit_cost = r1.json()["credit_estimate"]  # both same agent, same cost
        assert credits.used_credits == credit_cost * 2

    def test_run_agent_with_context_stored_in_job(self, client, db):
        """Context dict passed in request must be stored in job.input_data."""
        import json as _json
        user, token, credits = make_user(db)
        _with_starter_credits(db, user, credits)

        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                f"/api/agents/{STARTER_AGENT}/run",
                json={
                    "prompt": "Post about summer sale",
                    "context": {"brand": "Acme", "tone": "fun"},
                },
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK
        job_id = resp.json()["job_id"]

        job = db.query(AgentJob).filter(AgentJob.id == job_id).first()
        input_data = _json.loads(job.input_data)
        assert "prompt" in input_data
        assert "context" in input_data
        assert input_data["context"].get("brand") == "Acme"

    def test_job_retrieval_after_creation(self, client, db):
        """GET /api/agents/jobs/{job_id} should return the created job."""
        user, token, credits = make_user(db)
        _with_starter_credits(db, user, credits)

        with patch("app.routes.agents.send_approval_needed"):
            run_resp = client.post(
                f"/api/agents/{STARTER_AGENT}/run",
                json={"prompt": "Retrieve this job"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert run_resp.status_code == status.HTTP_200_OK
        job_id = run_resp.json()["job_id"]

        get_resp = client.get(
            f"/api/agents/jobs/{job_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_resp.status_code == status.HTTP_200_OK
        body = get_resp.json()
        # GET /api/agents/jobs/{id} returns "job_id" key (not "id")
        assert body["job_id"] == job_id

    def test_job_not_accessible_by_other_user(self, client, db):
        """Another user must not be able to retrieve a different user's job."""
        user1, token1, credits1 = make_user(db)
        _with_starter_credits(db, user1, credits1)
        user2, token2, credits2 = make_user(db)

        with patch("app.routes.agents.send_approval_needed"):
            run_resp = client.post(
                f"/api/agents/{STARTER_AGENT}/run",
                json={"prompt": "My private job"},
                headers={"Authorization": f"Bearer {token1}"},
            )
        assert run_resp.status_code == status.HTTP_200_OK
        job_id = run_resp.json()["job_id"]

        # User2 tries to access user1's job
        get_resp = client.get(
            f"/api/agents/jobs/{job_id}",
            headers={"Authorization": f"Bearer {token2}"},
        )
        # Should be 404 (not found in user2's workspace) or 403
        assert get_resp.status_code in (
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_agent_returns_expected_fields(self, client, db):
        """Run response must include job_id, agent_id, status, hitl_level, credit_estimate."""
        user, token, credits = make_user(db)
        _with_starter_credits(db, user, credits)

        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                f"/api/agents/{STARTER_AGENT}/run",
                json={"prompt": "Caption for our new product"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        for field in ("job_id", "agent_id", "status", "hitl_level", "credit_estimate"):
            assert field in body, f"Missing field: {field}"

    def test_jobs_list_shows_submitted_job(self, client, db):
        """GET /api/agents/jobs must include the job after it's submitted."""
        user, token, credits = make_user(db)
        _with_starter_credits(db, user, credits)

        with patch("app.routes.agents.send_approval_needed"):
            run_resp = client.post(
                f"/api/agents/{STARTER_AGENT}/run",
                json={"prompt": "List test post"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert run_resp.status_code == status.HTTP_200_OK
        job_id = run_resp.json()["job_id"]

        list_resp = client.get(
            "/api/agents/jobs",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert list_resp.status_code == status.HTTP_200_OK
        job_ids = [j["id"] for j in list_resp.json()["jobs"]]
        assert job_id in job_ids
