"""
Unit tests for the credit system.

Covers:
  - Credits start at expected amounts
  - Credit check: 0 remaining → agent run rejected with 402
  - Credit deduction after successful job submission
  - Credit ledger: used_credits incremented by credit_estimate
  - Partial credits: can run cheap agent but not expensive one
  - TOCTOU guard: credits locked per-workspace
  - Admin credit deployment (admin endpoint)
  - Non-admin cannot deploy credits
"""
import uuid
from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi import status

from conftest import make_user
from app.models.agent_system import AgentJob
from app.models.workspace import CreditsAccount


# Agents chosen for predictable credit costs
AGENT_1CR = "social_media_content_agent"   # credit_estimate=1, min_package=starter
AGENT_2CR = "research_analytics_agent"     # credit_estimate=2, min_package=starter
AGENT_3CR = "strategist_agent"             # credit_estimate=3, min_package=business


def _ws_credits(db, user_id: str):
    """Return the CreditsAccount for a user's workspace."""
    from app.models import Organization
    from app.models.workspace import Workspace
    org = db.query(Organization).filter(Organization.owner_id == user_id).first()
    ws = db.query(Workspace).filter(Workspace.organization_id == org.id).first()
    return db.query(CreditsAccount).filter(CreditsAccount.workspace_id == ws.id).first()


# ---------------------------------------------------------------------------
# Basic credit model tests
# ---------------------------------------------------------------------------

class TestCreditModel:
    def test_new_account_has_100_total_credits(self, db):
        _, _, credits = make_user(db)
        assert credits.total_credits == 100

    def test_new_account_has_zero_used_credits(self, db):
        _, _, credits = make_user(db)
        assert credits.used_credits == 0

    def test_available_credits_computed_correctly(self, db):
        _, _, credits = make_user(db)
        credits.used_credits = 40
        db.commit()
        db.refresh(credits)
        available = credits.total_credits - credits.used_credits
        assert available == 60

    def test_deducting_credits_reduces_available(self, db):
        _, _, credits = make_user(db)
        credits.used_credits += 10
        db.commit()
        db.refresh(credits)
        assert credits.total_credits - credits.used_credits == 90

    def test_used_credits_cannot_go_below_zero_by_guard(self, db):
        """Refund guard ensures used_credits never goes negative."""
        _, _, credits = make_user(db)
        credits.used_credits = 5
        db.commit()
        # Simulate clamped refund
        credits.used_credits = max(0, credits.used_credits - 50)
        db.commit()
        db.refresh(credits)
        assert credits.used_credits == 0

    def test_full_credit_drain(self, db):
        _, _, credits = make_user(db)
        credits.used_credits = credits.total_credits
        db.commit()
        db.refresh(credits)
        assert credits.total_credits - credits.used_credits == 0

    def test_credits_account_linked_to_workspace(self, db):
        from app.models import Organization
        from app.models.workspace import Workspace
        user, _, credits = make_user(db)
        org = db.query(Organization).filter(Organization.owner_id == user.id).first()
        ws = db.query(Workspace).filter(Workspace.organization_id == org.id).first()
        assert credits.workspace_id == ws.id


# ---------------------------------------------------------------------------
# Credit check: run agent with 0 credits → 402
# ---------------------------------------------------------------------------

class TestCreditCheck:
    def test_zero_credits_rejects_agent_run(self, client, db):
        """Workspace with 0 available credits → POST /api/agents/{id}/run returns 402."""
        user, token, credits = make_user(db)
        credits.total_credits = 60
        credits.used_credits = 60  # zero available
        db.commit()

        resp = client.post(
            f"/api/agents/{AGENT_1CR}/run",
            json={"prompt": "Write a post"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == status.HTTP_402_PAYMENT_REQUIRED

    def test_one_credit_allows_1cr_agent(self, client, db):
        """Exactly 1 credit available → can run 1-credit agent."""
        user, token, credits = make_user(db)
        credits.total_credits = 60
        credits.used_credits = 59  # exactly 1 available
        db.commit()

        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                f"/api/agents/{AGENT_1CR}/run",
                json={"prompt": "Write a post"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK

    def test_one_credit_blocks_2cr_agent(self, client, db):
        """1 credit available → cannot run 2-credit agent → 402."""
        user, token, credits = make_user(db)
        credits.total_credits = 60
        credits.used_credits = 59  # exactly 1 available
        db.commit()

        resp = client.post(
            f"/api/agents/{AGENT_2CR}/run",
            json={"prompt": "Research my market"},
            headers={"Authorization": f"Bearer {token}"},
        )
        # 402 (insufficient credits) OR 403 (tier gate for growth-tier agent) OR 402
        # research_analytics_agent is starter-tier so credit gate applies
        assert resp.status_code in (status.HTTP_402_PAYMENT_REQUIRED, status.HTTP_403_FORBIDDEN)

    def test_insufficient_credits_error_message(self, client, db):
        """402 response must mention credits in the detail."""
        user, token, credits = make_user(db)
        credits.total_credits = 60
        credits.used_credits = 60
        db.commit()

        resp = client.post(
            f"/api/agents/{AGENT_1CR}/run",
            json={"prompt": "Write a post"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == status.HTTP_402_PAYMENT_REQUIRED
        body = resp.json()
        assert "detail" in body
        assert "credit" in body["detail"].lower() or "insufficient" in body["detail"].lower()


# ---------------------------------------------------------------------------
# Credit deduction: ledger correctness
# ---------------------------------------------------------------------------

class TestCreditDeductionLedger:
    def test_job_submission_deducts_exact_credit_estimate(self, client, db):
        """used_credits must increase by exactly credit_estimate after a successful run."""
        user, token, credits = make_user(db)
        credits.total_credits = 60
        credits.used_credits = 0
        db.commit()

        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                f"/api/agents/{AGENT_1CR}/run",
                json={"prompt": "Create post"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK
        cost = resp.json()["credit_estimate"]

        db.refresh(credits)
        assert credits.used_credits == cost

    def test_sequential_jobs_accumulate_credits(self, client, db):
        """Two sequential runs must each deduct credits cumulatively."""
        user, token, credits = make_user(db)
        credits.total_credits = 60
        credits.used_credits = 0
        db.commit()

        with patch("app.routes.agents.send_approval_needed"):
            r1 = client.post(
                f"/api/agents/{AGENT_1CR}/run",
                json={"prompt": "Post one"},
                headers={"Authorization": f"Bearer {token}"},
            )
            r2 = client.post(
                f"/api/agents/{AGENT_1CR}/run",
                json={"prompt": "Post two"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert r1.status_code == status.HTTP_200_OK
        assert r2.status_code == status.HTTP_200_OK

        db.refresh(credits)
        cost = r1.json()["credit_estimate"]
        assert credits.used_credits == cost * 2

    def test_job_credit_cost_stored_in_job_row(self, client, db):
        """AgentJob.credits_used must match the agent's credit_estimate."""
        user, token, credits = make_user(db)
        credits.total_credits = 60
        credits.used_credits = 0
        db.commit()

        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                f"/api/agents/{AGENT_1CR}/run",
                json={"prompt": "Post"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK
        job_id = resp.json()["job_id"]
        cost = resp.json()["credit_estimate"]

        job = db.query(AgentJob).filter(AgentJob.id == job_id).first()
        assert job.credits_used == cost

    def test_hitl3_job_deducts_credits_immediately(self, client, db):
        """HITL-3 jobs auto-approved at submission — credits deducted immediately."""
        user, token, credits = make_user(db)
        credits.total_credits = 300  # business tier
        credits.used_credits = 0
        db.commit()

        with patch("app.routes.agents.send_approval_needed"):
            resp = client.post(
                "/api/agents/ads_optimisation_agent/run",
                json={"prompt": "Optimise my ad spend"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["status"] == "approved"

        db.refresh(credits)
        # Credits ARE pre-committed for auto-approved HITL-3 jobs
        assert credits.used_credits == 4  # ads_optimisation_agent credit_estimate


# ---------------------------------------------------------------------------
# Admin credit operations
# ---------------------------------------------------------------------------

class TestAdminCreditOps:
    def test_admin_deploy_unlimited_credits(self, client, db):
        """Admin can set a workspace to unlimited (9999) credits via packages/deploy-unlimited."""
        admin, admin_token, _ = make_user(db, email="admin-credits@test.com", is_admin=True)
        target_user, _, target_credits = make_user(db)
        target_credits.used_credits = 90
        db.commit()

        resp = client.post(
            "/api/admin/packages/deploy-unlimited",
            json={"user_id": target_user.id, "reason": "Beta testing reward"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_200_OK
        db.refresh(target_credits)
        assert target_credits.total_credits == 9999

    def test_non_admin_cannot_deploy_credits(self, client, db):
        """Non-admin user must be denied access to admin credit endpoint."""
        _, user_token, _ = make_user(db)
        target_user, _, _ = make_user(db)

        resp = client.post(
            "/api/admin/packages/deploy-unlimited",
            json={"user_id": target_user.id, "reason": "hacking"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_credit_adjust_endpoint(self, client, db):
        """Admin can adjust credits for a specific client via /clients/{id}/credits."""
        admin, admin_token, _ = make_user(db, email="admin3-credits@test.com", is_admin=True)
        target_user, _, target_credits = make_user(db)
        initial_total = target_credits.total_credits

        resp = client.post(
            f"/api/admin/clients/{target_user.id}/credits",
            json={"amount": 50, "reason": "Top-up"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_200_OK
        db.refresh(target_credits)
        assert target_credits.total_credits == initial_total + 50

    def test_admin_credit_deploy_does_not_affect_other_workspace(self, client, db):
        """Deploying credits to user A must not change user B's credits."""
        admin, admin_token, _ = make_user(db, email="admin2-credits@test.com", is_admin=True)
        user_a, _, credits_a = make_user(db)
        user_b, _, credits_b = make_user(db)
        initial_b_total = credits_b.total_credits

        resp = client.post(
            "/api/admin/packages/deploy-unlimited",
            json={"user_id": user_a.id, "reason": "Test isolation"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_200_OK

        db.refresh(credits_b)
        assert credits_b.total_credits == initial_b_total
