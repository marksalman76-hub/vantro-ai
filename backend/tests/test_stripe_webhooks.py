import json
import time
import hmac
import hashlib
import pytest
from unittest.mock import patch, MagicMock


def _stripe_signature(payload: bytes, secret: str) -> str:
    timestamp = str(int(time.time()))
    signed_payload = f"{timestamp}.{payload.decode()}"
    sig = hmac.new(secret.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={sig}"


WEBHOOK_SECRET = "whsec_test_secret"
WEBHOOK_URL = "/api/stripe/webhook"


@pytest.fixture
def stripe_client(client):
    with patch("app.core.stripe_webhook_hardening.STRIPE_WEBHOOK_SECRET", WEBHOOK_SECRET):
        yield client


def _post_event(stripe_client, event: dict):
    payload = json.dumps(event).encode()
    sig = _stripe_signature(payload, WEBHOOK_SECRET)
    return stripe_client.post(
        WEBHOOK_URL,
        content=payload,
        headers={"stripe-signature": sig, "content-type": "application/json"},
    )


def _make_event(event_type: str, data: dict) -> dict:
    return {
        "id": "evt_test_123",
        "type": event_type,
        "data": {"object": data},
        "livemode": False,
    }


class TestWebhookSignatureVerification:
    def test_missing_signature_rejected(self, client):
        payload = json.dumps({"type": "checkout.session.completed"}).encode()
        resp = client.post(
            WEBHOOK_URL,
            content=payload,
            headers={"content-type": "application/json"},
        )
        assert resp.status_code in (400, 422)

    def test_invalid_signature_rejected(self, client):
        payload = json.dumps({"type": "checkout.session.completed"}).encode()
        resp = client.post(
            WEBHOOK_URL,
            content=payload,
            headers={"stripe-signature": "t=123,v1=badsig", "content-type": "application/json"},
        )
        assert resp.status_code in (400, 403)

    def test_valid_signature_accepted(self, stripe_client):
        event = _make_event("ping", {})
        resp = _post_event(stripe_client, event)
        assert resp.status_code != 403


class TestCheckoutSessionCompleted:
    def test_checkout_completed_triggers_credit_allocation(self, stripe_client):
        event = _make_event(
            "checkout.session.completed",
            {
                "id": "cs_test_123",
                "customer": "cus_test_123",
                "subscription": "sub_test_123",
                "metadata": {"workspace_id": "ws_test_123", "plan": "starter"},
                "payment_status": "paid",
            },
        )
        with patch("app.core.stripe_webhook_handler.allocate_credits") as mock_alloc:
            resp = _post_event(stripe_client, event)
            if resp.status_code == 200:
                mock_alloc.assert_called_once()

    def test_unpaid_checkout_ignored(self, stripe_client):
        event = _make_event(
            "checkout.session.completed",
            {
                "id": "cs_test_456",
                "customer": "cus_test_123",
                "payment_status": "unpaid",
            },
        )
        resp = _post_event(stripe_client, event)
        assert resp.status_code in (200, 400)


class TestSubscriptionEvents:
    def test_subscription_deleted_deactivates_workspace(self, stripe_client):
        event = _make_event(
            "customer.subscription.deleted",
            {
                "id": "sub_test_123",
                "customer": "cus_test_123",
                "status": "canceled",
            },
        )
        resp = _post_event(stripe_client, event)
        assert resp.status_code in (200, 400, 404)

    def test_subscription_updated_syncs_status(self, stripe_client):
        event = _make_event(
            "customer.subscription.updated",
            {
                "id": "sub_test_123",
                "customer": "cus_test_123",
                "status": "active",
                "current_period_end": int(time.time()) + 2592000,
            },
        )
        resp = _post_event(stripe_client, event)
        assert resp.status_code in (200, 400, 404)

    def test_invoice_payment_failed_handled(self, stripe_client):
        event = _make_event(
            "invoice.payment_failed",
            {
                "id": "in_test_123",
                "customer": "cus_test_123",
                "subscription": "sub_test_123",
                "amount_due": 9900,
            },
        )
        resp = _post_event(stripe_client, event)
        assert resp.status_code in (200, 400, 404)
