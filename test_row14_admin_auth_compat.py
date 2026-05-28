from types import SimpleNamespace
from backend.app.runtime.ai_media_session_auth_compat import validate_ai_media_admin_session_compatibility


class FakeHeaders(dict):
    def get(self, key, default=None):
        return super().get(key, default)


class FakeRequest:
    def __init__(self, path, method="GET", headers=None):
        self.url = SimpleNamespace(path=path)
        self.method = method
        self.headers = FakeHeaders(headers or {})


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


token = "local-test-admin-token"

import os
os.environ["ADMIN_PLATFORM_TOKEN"] = token

for path, method in [
    ("/admin/provider-action-readiness", "GET"),
    ("/admin/provider-action-readiness/evaluate", "POST"),
]:
    request = FakeRequest(
        path=path,
        method=method,
        headers={
            "x-actor-role": "owner_admin",
            "x-admin-token": token,
        },
    )
    result = validate_ai_media_admin_session_compatibility(request)
    assert_true(result["allowed"] is True, f"{path} should allow owner_admin x-admin-token")
    assert_true(result["owner_admin_only"] is True, f"{path} should remain owner/admin only")
    assert_true(result["client_public_access_blocked"] is True, f"{path} should block public client access")
    assert_true(result["governance_preserved"] is True, f"{path} should preserve governance")

bad_role = validate_ai_media_admin_session_compatibility(FakeRequest(
    path="/admin/provider-action-readiness",
    method="GET",
    headers={
        "x-actor-role": "client",
        "x-admin-token": token,
    },
))
assert_true(bad_role["allowed"] is False, "client role must remain blocked")

bad_token = validate_ai_media_admin_session_compatibility(FakeRequest(
    path="/admin/provider-action-readiness",
    method="GET",
    headers={
        "x-actor-role": "owner_admin",
        "x-admin-token": "wrong-token",
    },
))
assert_true(bad_token["allowed"] is False, "wrong token must remain blocked")

public_path = validate_ai_media_admin_session_compatibility(FakeRequest(
    path="/public/test",
    method="GET",
    headers={
        "x-actor-role": "owner_admin",
        "x-admin-token": token,
    },
))
assert_true(public_path["allowed"] is False, "unregistered route must remain blocked")

print("ROW14_ADMIN_AUTH_COMPAT_TEST_PASSED")
