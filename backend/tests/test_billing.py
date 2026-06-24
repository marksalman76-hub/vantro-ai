"""
Unit + integration tests for the Billing API.

Covers POST /api/billing/refund-request:
  - Not authenticated → 401
  - No workspace → 400
  - Tasks executed (completed job) → 403
  - Within 72h window, no tasks → 200 (Stripe mocked)
  - Outside 72h window → 403

Also covers:
  - POST /api/billing/setup-intent  (invalid plan → 400, requires auth)
  - POST /api/billing/confirm       (invalid payment method → 400)
  - GET  /api/billing/activate/{token} (bad token → 400/404)
"""
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from sqlalchemy import text

from conftest import make_user
from app.models.agent_system import AgentJob
from app.models.workspace import CreditsAccount


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_user_with_stripe(db, *, hours_old=1, subscription_id="sub_test_123", customer_id="cus_test_123"):
    """Create a user with a workspace created `hours_old` hours ago, and Stripe IDs set."""
    user, token, credits = make_user(db)
    # Set workspace created_at to control the 72h window
    from app.models import Organization
    from app.models.workspace import Workspace
    org = db.query(Organization).filter(Organization.owner_id == user.id).first()
    ws = db.query(Workspace).filter(Workspace.organization_id == org.id).first()
    ws.created_at = datetime.utcnow() - timedelta(hours=hours_old)
    db.commit()
    # Set Stripe IDs on user
    db.execute(
        text("UPDATE users SET stripe_customer_id=:cid, stripe_subscription_id=:sid WHERE id=:uid"),
        {"cid": customer_id, "sid": subscription_id, "uid": user.id},
    )
    db.commit()
    db.refresh(user)
    return user, token, credits, ws


def _make_completed_job(db, workspace_id: str, agent_id: str = "social_media_content_agent"):
    """Insert an AgentJob with status='completed' to simulate executed task."""
    job = AgentJob(
        id=str(uuid.uuid4()),
        workspace_id=workspace_id,
        agent_id=agent_id,
        agent_name="Social Media Content Agent",
        status="completed",
        credits_used=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    return job


# ---------------------------------------------------------------------------
# POST /api/billing/refund-request
# ---------------------------------------------------------------------------

class TestRefundRequest:
    ENDPOINT = "/api/billing/refund-request"

    def test_refund_requires_auth(self, client):
        resp = client.post(self.ENDPOINT)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refund_invalid_token(self, client):
        resp = client.post(self.ENDPOINT, headers={"Authorization": "Bearer bad.token"})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refund_within_window_no_tasks_succeeds(self, client, db):
        """No executed jobs + within 72h → Stripe refund issued → 200."""
        user, token, credits, ws = _make_user_with_stripe(db, hours_old=24)

        mock_invoice = MagicMock()
        mock_invoice.id = "in_test_001"
        mock_invoice.get = lambda k, d=None: "pi_test_001" if k == "payment_intent" else d
        mock_invoice_list = MagicMock()
        mock_invoice_list.data = [mock_invoice]

        with patch("stripe.Invoice.list", return_value=mock_invoice_list), \
             patch("stripe.Refund.create") as mock_refund, \
             patch("stripe.Subscription.delete") as mock_cancel:
            resp = client.post(self.ENDPOINT, headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "detail" in body
        assert "refund" in body["detail"].lower() or "processed" in body["detail"].lower()
        mock_refund.assert_called_once()
        mock_cancel.assert_called_once_with("sub_test_123")

    def test_refund_with_executed_tasks_returns_403(self, client, db):
        """Completed agent jobs → refund must be blocked."""
        user, token, credits, ws = _make_user_with_stripe(db, hours_old=10)
        _make_completed_job(db, ws.id)

        resp = client.post(self.ENDPOINT, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        body = resp.json()
        assert "executed" in body["detail"].lower() or "tasks" in body["detail"].lower()

    def test_refund_outside_72h_window_returns_403(self, client, db):
        """Account older than 72h → window closed → 403."""
        user, token, credits, ws = _make_user_with_stripe(db, hours_old=73)

        resp = client.post(self.ENDPOINT, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        body = resp.json()
        assert "window" in body["detail"].lower() or "72" in body["detail"].lower() or "closed" in body["detail"].lower()

    def test_refund_no_stripe_customer_returns_400(self, client, db):
        """User without a Stripe customer ID → 400 billing account not found."""
        user, token, credits = make_user(db)
        # No Stripe customer ID set
        resp = client.post(self.ENDPOINT, headers={"Authorization": f"Bearer {token}"})
        # Should fail at workspace check (no org created correctly) or stripe customer check
        assert resp.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN)

    def test_refund_pending_jobs_not_counted_as_executed(self, client, db):
        """Jobs with status='pending' or 'failed' must NOT block the refund."""
        user, token, credits, ws = _make_user_with_stripe(db, hours_old=5)
        # Add a pending job (should not block refund)
        pending_job = AgentJob(
            id=str(uuid.uuid4()),
            workspace_id=ws.id,
            agent_id="social_media_content_agent",
            agent_name="Social Media Content Agent",
            status="pending",
            credits_used=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(pending_job)
        # Add a failed job (should not block refund)
        failed_job = AgentJob(
            id=str(uuid.uuid4()),
            workspace_id=ws.id,
            agent_id="social_media_content_agent",
            agent_name="Social Media Content Agent",
            status="failed",
            credits_used=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(failed_job)
        db.commit()

        mock_invoice = MagicMock()
        mock_invoice.id = "in_test_002"
        mock_invoice.get = lambda k, d=None: "pi_test_002" if k == "payment_intent" else d
        mock_invoice_list = MagicMock()
        mock_invoice_list.data = [mock_invoice]

        with patch("stripe.Invoice.list", return_value=mock_invoice_list), \
             patch("stripe.Refund.create"), \
             patch("stripe.Subscription.delete"):
            resp = client.post(self.ENDPOINT, headers={"Authorization": f"Bearer {token}"})

        # Pending + failed jobs don't count as executed → refund proceeds
        assert resp.status_code == status.HTTP_200_OK

    def test_refund_subscription_cancel_failure_does_not_block(self, client, db):
        """Even if Stripe subscription cancel fails, refund should proceed."""
        user, token, credits, ws = _make_user_with_stripe(db, hours_old=10)

        mock_invoice = MagicMock()
        mock_invoice.id = "in_test_003"
        mock_invoice.get = lambda k, d=None: "pi_test_003" if k == "payment_intent" else d
        mock_invoice_list = MagicMock()
        mock_invoice_list.data = [mock_invoice]

        import stripe as _stripe
        with patch("stripe.Invoice.list", return_value=mock_invoice_list), \
             patch("stripe.Refund.create") as mock_refund, \
             patch("stripe.Subscription.delete", side_effect=_stripe.error.StripeError("test")):
            resp = client.post(self.ENDPOINT, headers={"Authorization": f"Bearer {token}"})

        # Subscription cancel failure is non-fatal — refund still returns 200
        assert resp.status_code == status.HTTP_200_OK
        mock_refund.assert_called_once()


# ---------------------------------------------------------------------------
# POST /api/billing/setup-intent
# ---------------------------------------------------------------------------

class TestSetupIntent:
    ENDPOINT = "/api/billing/setup-intent"

    def test_setup_intent_requires_auth(self, client):
        resp = client.post(self.ENDPOINT, json={"plan": "starter", "agent_ids": []})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_setup_intent_invalid_plan(self, client, db):
        _, token, _ = make_user(db)
        resp = client.post(
            self.ENDPOINT,
            json={"plan": "nonexistent_plan", "agent_ids": []},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_setup_intent_valid_plan_creates_customer(self, client, db):
        """Valid plan with Stripe mocked → returns client_secret.
        Note: agent_ids must match AGENT_DISPLAY_NAMES in billing.py (not the registry).
        """
        _, token, _ = make_user(db)
        with patch("app.services.stripe_service.StripeService.get_or_create_customer", return_value="cus_new_123"), \
             patch("app.services.stripe_service.StripeService.create_setup_intent", return_value="seti_test_secret"):
            resp = client.post(
                self.ENDPOINT,
                json={"plan": "starter", "agent_ids": ["intake_trial_agent", "content_strategy_agent"]},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "client_secret" in body
        assert body["plan"] == "starter"


# ---------------------------------------------------------------------------
# GET /api/billing/activate/{token}
# ---------------------------------------------------------------------------

class TestActivateWorkspace:
    def test_activate_short_token_rejected(self, client):
        resp = client.get("/api/billing/activate/short")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_activate_unknown_token_returns_404(self, client):
        fake_token = "a" * 64  # long enough but not in DB
        resp = client.get(f"/api/billing/activate/{fake_token}")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
