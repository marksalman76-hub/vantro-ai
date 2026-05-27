
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

status = client.get("/provider-execution-admin-visibility/status")
assert status.status_code == 200
status_json = status.json()

assert status_json["success"] is True
assert status_json["provider_execution_admin_visibility_ready"] is True
assert status_json["credential_values_exposed"] is False

summary = client.get("/provider-execution-admin-visibility/summary")
assert summary.status_code == 200
summary_json = summary.json()

assert summary_json["success"] is True
assert summary_json["provider_execution_admin_visibility_ready"] is True
assert "summary" in summary_json
assert summary_json["credential_values_exposed"] is False

print("PROVIDER_EXECUTION_ADMIN_VISIBILITY_ROUTES_TESTS_PASSED")
print("status_ready", status_json["provider_execution_admin_visibility_ready"])
print("summary_ready", summary_json["provider_execution_admin_visibility_ready"])
print("credential_values_exposed", summary_json["credential_values_exposed"])
