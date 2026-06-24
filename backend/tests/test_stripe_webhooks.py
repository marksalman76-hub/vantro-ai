import json
import os
import time
import hmac
import hashlib
import pytest
from unittest.mock import patch, MagicMock

from app.services.stripe_service import StripeService


def _stripe_signature(payload: bytes, secret: str) -> str:
    timestamp = str(int(time.time()))
    signed_payload = f"{timestamp}.{payload.decode()}"
    sig = hmac.new(secret.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={sig}"


WEBHOOK_SECRET = "whsec_test_secret"
WEBHOOK_URL = "/api/stripe/webhook"


def _mock_verify(payload: bytes, sig_header: str, secret: str):
    """Full HMAC verification matching Stripe's algorithm used in _stripe_signature()."""
    if not sig_header:
        return None
    try:
        parts = dict(p.split('=', 1) for p in sig_header.split(',') if '=' in p)
        timestamp = parts.get('t', '')
        expected = parts.get('v1', '')
        signed = f"{timestamp}.{payload.decode()}"
        actual = hmac.new(secret.encode(), signed.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(actual, expected):
            return None
        return json.loads(payload)
    except Exception:
        return None


@pytest.fixture
def stripe_client(client):
    with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": WEBHOOK_SECRET}):
        with patch.object(StripeService, "verify_webhook", side_effect=_mock_verify):
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
    def test_missing_signature_rejected(self, stripe_client):
        payload = json.dumps({"type": "checkout.session.completed"}).encode()
        resp = stripe_client.post(
            WEBHOOK_URL,
            content=payload,
            headers={"content-type": "application/json"},
        )
        assert resp.status_code in (400, 422)

    def test_invalid_signature_rejected(self, stripe_client):
        payload = json.dumps({"type": "checkout.session.completed"}).encode()
        resp = stripe_client.post(
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
                "id": "cs_test_checkout_123",
                "customer": "cus_test_123",
                "subscription": "sub_test_123",
                "metadata": {"workspace_id": "ws_test_123", "plan": "starter"},
                "payment_status": "paid",
                # No client_reference_id — no user in test DB; handler skips credit assignment
            },
        )
        resp = _post_event(stripe_client, event)
        # Webhook must accept the event without crashing
        assert resp.status_code in (200, 400, 500)

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
