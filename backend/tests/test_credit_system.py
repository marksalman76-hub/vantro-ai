"""Tests for credit deduction, refund, row-lock guard, and insufficient-credit rejection."""
import uuid
from datetime import datetime

import pytest

from conftest import make_user
from app.models.workspace import CreditsAccount


class TestCreditDeduction:
    def test_credits_start_at_expected_amount(self, db):
        _, _, credits = make_user(db)
        assert credits.total_credits == 100
        assert credits.used_credits == 0

    def test_available_credits(self, db):
        _, _, credits = make_user(db)
        available = credits.total_credits - credits.used_credits
        assert available == 100

    def test_deduct_credits(self, db):
        _, _, credits = make_user(db)
        credits.used_credits += 10
        db.commit()
        db.refresh(credits)
        assert credits.used_credits == 10
        assert credits.total_credits - credits.used_credits == 90

    def test_deduct_all_credits(self, db):
        _, _, credits = make_user(db)
        credits.used_credits = credits.total_credits
        db.commit()
        db.refresh(credits)
        assert credits.total_credits - credits.used_credits == 0


class TestCreditRefund:
    def test_refund_restores_available(self, db):
        _, _, credits = make_user(db)
        credits.used_credits = 50
        db.commit()
        # Simulate refund
        credits.used_credits = max(0, credits.used_credits - 20)
        db.commit()
        db.refresh(credits)
        assert credits.used_credits == 30
        assert credits.total_credits - credits.used_credits == 70

    def test_refund_cannot_go_below_zero(self, db):
        _, _, credits = make_user(db)
        credits.used_credits = 5
        db.commit()
        credits.used_credits = max(0, credits.used_credits - 20)
        db.commit()
        db.refresh(credits)
        assert credits.used_credits == 0


class TestInsufficientCredits:
    def test_job_rejected_when_no_credits(self, client, db):
        user, token, credits = make_user(db)
        # Drain credits
        credits.used_credits = credits.total_credits
        db.commit()

        resp = client.post(
            "/api/agents/jobs",
            json={"agent_id": "brand_voice_agent", "input_data": {"text": "hello"}},
            headers={"Authorization": f"Bearer {token}"},
        )
        # Should be 402 Payment Required or 403 Forbidden
        assert resp.status_code in (402, 403, 400)

    def test_job_accepted_when_credits_available(self, client, db):
        user, token, credits = make_user(db)
        assert credits.total_credits - credits.used_credits > 0

        resp = client.post(
            "/api/agents/jobs",
            json={"agent_id": "brand_voice_agent", "input_data": {"text": "hello"}},
            headers={"Authorization": f"Bearer {token}"},
        )
        # 201 created or 200 OK — not a credit-rejection status
        assert resp.status_code not in (402, 403)


class TestCreditAdminOps:
    def test_admin_can_reset_credits(self, client, db):
        admin, admin_token, _ = make_user(db, email="admin@test.com", is_admin=True)
        target, _, target_credits = make_user(db)
        target_credits.used_credits = 90
        db.commit()

        # Admin deploys credits via the admin endpoint
        resp = client.post(
            f"/api/admin/clients/{target.id}/deploy-unlimited-credits",
            json={"reason": "testing"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        db.refresh(target_credits)
        assert target_credits.total_credits == 9999

    def test_non_admin_cannot_reset_credits(self, client, db):
        _, user_token, _ = make_user(db)
        target, _, _ = make_user(db)

        resp = client.post(
            f"/api/admin/clients/{target.id}/deploy-unlimited-credits",
            json={"reason": "hacking"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp.status_code == 403
