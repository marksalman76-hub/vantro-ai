import os
from fastapi.testclient import TestClient
from backend.app.main import app

os.environ["ADMIN_PLATFORM_TOKEN"] = "test-admin-token-provider-actions"

client = TestClient(app)

routes = [
    "/provider-execution-admin-visibility/actions/retry",
    "/provider-execution-admin-visibility/actions/requeue",
    "/provider-execution-admin-visibility/actions/cancel",
]

for route in routes:
    unauthorised = client.post(route, json={"job_id": "job_test_001"})
    assert unauthorised.status_code == 401, (route, unauthorised.status_code, unauthorised.text)

    authorised = client.post(
        route,
        headers={"Authorization": "Bearer test-admin-token-provider-actions"},
        json={"job_id": "job_test_001", "reason": "test governed action"},
    )
    assert authorised.status_code == 200, (route, authorised.status_code, authorised.text)
    payload = authorised.json()
    assert payload["ready"] is True
    assert payload["accepted"] is True
    assert payload["governed"] is True
    assert payload["owner_authority_preserved"] is True
    assert payload["credential_values_exposed"] is False
    assert payload["customer_safe"] is True
    assert payload["job_id"] == "job_test_001"

print("PROVIDER_EXECUTION_GOVERNED_ACTIONS_BACKEND_TESTS_PASSED")
print("protected_action_routes_ready", True)
print("unauthorised_access_blocked", True)
print("credential_values_exposed", False)
