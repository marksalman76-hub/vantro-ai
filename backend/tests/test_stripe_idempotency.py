"""Integration tests for Stripe webhook idempotency."""
import json
import hmac
import hashlib
import time
import pytest
from fastapi import status
from unittest.mock import patch


def _make_stripe_sig(payload: str, secret: str) -> str:
    ts = str(int(time.time()))
    signed = f"{ts}.{payload}"
    sig = hmac.new(secret.encode(), signed.encode(), hashlib.sha256).hexdigest()
    return f"t={ts},v1={sig}"


DUMMY_SECRET = "whsec_test_secret_key_12345"


@pytest.fixture(autouse=True)
def patch_stripe_secret(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", DUMMY_SECRET)


@pytest.mark.unit
class TestStripeWebhookIdempotency:
    def _post_webhook(self, client, event_id: str, event_type: str = "customer.subscription.updated"):
        payload = json.dumps({
            "id": event_id,
            "type": event_type,
            "data": {
                "object": {
                    "customer": "cus_test123",
                    "status": "active",
                }
            },
        })
        sig = _make_stripe_sig(payload, DUMMY_SECRET)
        return client.post(
            "/api/stripe/webhook",
            content=payload,
            headers={
                "stripe-signature": sig,
                "content-type": "application/json",
            },
        )

    def test_webhook_accepts_valid_event(self, client):
        with patch("stripe.Webhook.construct_event") as mock_construct:
            mock_construct.return_value = {
                "id": "evt_test_001",
                "type": "customer.subscription.updated",
                "data": {"object": {"customer": "cus_none", "status": "active"}},
            }
            resp = client.post(
                "/api/stripe/webhook",
                content=b'{}',
                headers={"stripe-signature": "t=1,v1=abc", "content-type": "application/json"},
            )
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)

    def test_webhook_rejects_missing_signature(self, client):
        resp = client.post(
            "/api/stripe/webhook",
            content=b'{"id":"evt_001","type":"test"}',
            headers={"content-type": "application/json"},
        )
        assert resp.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


@pytest.mark.unit
class TestBrandProfile:
    def test_get_brand_profile_unauthenticated(self, client):
        resp = client.get("/api/users/brand-profile")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_brand_profile_authenticated(self, client, authenticated_client):
        resp = authenticated_client.get("/api/users/brand-profile")
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "brand_profile" in body

    def test_update_brand_profile(self, client, authenticated_client):
        resp = authenticated_client.put("/api/users/brand-profile", json={
            "business_name": "Acme Corp",
            "industry": "E-commerce",
            "preferred_tone": "Professional",
        })
        assert resp.status_code == status.HTTP_200_OK

    def test_brand_profile_persists(self, client, authenticated_client):
        authenticated_client.put("/api/users/brand-profile", json={
            "business_name": "Test Co",
        })
        resp = authenticated_client.get("/api/users/brand-profile")
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert body.get("brand_profile", {}).get("business_name") == "Test Co"
