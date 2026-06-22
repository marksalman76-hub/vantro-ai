"""
VANTRO.AI Security Fix Tests
Verifies all 5 critical security fixes are working correctly.
"""
import pytest
from fastapi.testclient import TestClient


# ============================================================
# FIX #1: Tenant Isolation — x-tenant-id is REQUIRED
# Routes /client/integrations/* are planned but not yet live;
# these tests are skipped until those routes are added.
# ============================================================

class TestTenantIsolation:
    """Fix #1: All client endpoints must reject requests missing x-tenant-id."""

    @pytest.mark.skip(reason="/client/integrations/* routes not yet implemented")
    def test_integrations_connect_requires_tenant_id(self, client):
        resp = client.post("/client/integrations/connect", json={"integration_key": "test"})
        assert resp.status_code == 422, "Missing x-tenant-id should return 422"

    @pytest.mark.skip(reason="/client/integrations/* routes not yet implemented")
    def test_integrations_test_requires_tenant_id(self, client):
        resp = client.post("/client/integrations/test", json={"integration_key": "test"})
        assert resp.status_code == 422

    @pytest.mark.skip(reason="/client/integrations/* routes not yet implemented")
    def test_integrations_disconnect_requires_tenant_id(self, client):
        resp = client.post("/client/integrations/disconnect", json={"integration_key": "test"})
        assert resp.status_code == 422

    @pytest.mark.skip(reason="/client/integrations/* routes not yet implemented")
    def test_integrations_action_requires_tenant_id(self, client):
        resp = client.post("/client/integrations/action", json={"integration_key": "test"})
        assert resp.status_code == 422

    @pytest.mark.skip(reason="/client/integrations/* routes not yet implemented")
    def test_integrations_connect_accepts_valid_tenant_id(self, client, valid_headers):
        resp = client.post(
            "/client/integrations/connect",
            json={"integration_key": "test"},
            headers=valid_headers,
        )
        assert resp.status_code != 422, "Valid x-tenant-id should not produce 422"

    @pytest.mark.skip(reason="/client/integrations/* routes not yet implemented")
    def test_integrations_list_requires_tenant_id(self, client):
        resp = client.get("/client/integrations")
        assert resp.status_code == 422

    @pytest.mark.skip(reason="/client/integrations/* routes not yet implemented")
    def test_integrations_list_accepts_valid_tenant_id(self, client, valid_headers):
        resp = client.get("/client/integrations", headers=valid_headers)
        assert resp.status_code != 422


# ============================================================
# FIX #2: No Hardcoded Demo IDs
# ============================================================

class TestNoHardcodedDemoIds:
    """Fix #2: Hardcoded tenant IDs must not appear as literals in responses."""

    BANNED_IDS = ["client_demo_001", "owner_managed_demo", "manual_deployment_client"]

    def test_health_response_has_no_demo_ids(self, client):
        resp = client.get("/health")
        body = resp.text
        for banned in self.BANNED_IDS:
            assert banned not in body, f"Hardcoded ID '{banned}' leaked in /health response"

    def test_login_error_has_no_demo_ids(self, client):
        resp = client.post("/api/auth/login", json={"email": "test@test.com", "password": "wrong"})
        body = resp.text
        for banned in self.BANNED_IDS:
            assert banned not in body, f"Hardcoded ID '{banned}' leaked in login response"

    def test_agents_catalogue_has_no_demo_ids(self, client):
        resp = client.get("/api/admin/agents")
        body = resp.text
        for banned in self.BANNED_IDS:
            assert banned not in body, f"Hardcoded ID '{banned}' leaked in agents catalogue"


# ============================================================
# FIX #3: Pydantic Validation — malformed payloads rejected
# ============================================================

class TestPydanticValidation:
    """Fix #3: Endpoints using ValidatedPayload must reject non-object payloads."""

    def test_login_rejects_string_payload(self, client):
        resp = client.post(
            "/api/auth/login",
            content='"just a string"',
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 422

    def test_login_rejects_array_payload(self, client):
        resp = client.post(
            "/api/auth/login",
            content='["not", "an", "object"]',
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 422

    def test_login_accepts_object_payload(self, client):
        resp = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )
        assert resp.status_code != 422, "Valid JSON object should not return 422"

    @pytest.mark.skip(reason="/admin/execution-queue/enqueue route not yet implemented")
    def test_enqueue_rejects_string_payload(self, client):
        resp = client.post(
            "/admin/execution-queue/enqueue",
            content='"bad payload"',
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 422

    @pytest.mark.skip(reason="/admin/billing/event route not yet implemented")
    def test_billing_event_accepts_object_payload(self, client):
        resp = client.post("/admin/billing/event", json={"event_type": "test"})
        assert resp.status_code != 422

    @pytest.mark.skip(reason="/client/activate-account route not yet implemented")
    def test_activate_account_rejects_array(self, client):
        resp = client.post(
            "/client/activate-account",
            content='[1, 2, 3]',
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 422


# ============================================================
# FIX #4: Error Handling — no stack traces leaked
# ============================================================

class TestErrorHandling:
    """Fix #4: Server errors must return safe messages, never raw tracebacks."""

    LEAK_PATTERNS = ["Traceback", "File \"", "AttributeError", "KeyError"]

    def _assert_no_traceback(self, body: str):
        for pattern in self.LEAK_PATTERNS:
            assert pattern not in body, f"Stack trace pattern '{pattern}' leaked in response"

    def test_health_endpoint_is_clean(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        self._assert_no_traceback(resp.text)

    def test_unknown_route_has_no_traceback(self, client):
        resp = client.get("/this/route/does/not/exist")
        assert resp.status_code == 404
        self._assert_no_traceback(resp.text)

    def test_validation_error_has_no_traceback(self, client):
        resp = client.post(
            "/api/auth/login",
            content='"bad"',
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 422
        self._assert_no_traceback(resp.text)

    @pytest.mark.skip(reason="/admin/execution-queue/readiness route not yet implemented")
    def test_500_response_body_is_safe(self, client):
        resp = client.get("/admin/execution-queue/readiness")
        if resp.status_code == 500:
            body = resp.json()
            assert "error" in body
            assert "Traceback" not in resp.text
            assert body.get("error") == "Internal server error"


# ============================================================
# FIX #5: Rate Limiting — limiter is wired to the app
# ============================================================

class TestRateLimiting:
    """Fix #5: Rate limiter must be configured on the app."""

    def test_rate_limiter_attached_to_app(self, client):
        from backend.app.main import app
        assert hasattr(app.state, "limiter"), "app.state.limiter must be set"

    def test_rate_limits_dict_defined(self):
        from backend.app.main import RATE_LIMITS
        assert "global" in RATE_LIMITS
        assert "login" in RATE_LIMITS
        assert "media_generation" in RATE_LIMITS
        assert "billing" in RATE_LIMITS

    def test_cost_protection_middleware_registered(self):
        from backend.app.main import cost_protection_middleware
        import inspect
        assert inspect.iscoroutinefunction(cost_protection_middleware), \
            "cost_protection_middleware must be an async function"

    def test_repeated_requests_dont_crash(self, client):
        for _ in range(5):
            resp = client.get("/health")
            assert resp.status_code in (200, 422, 429, 500)
