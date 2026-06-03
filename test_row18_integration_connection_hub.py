from pathlib import Path
import re

ROOT = Path.cwd()

required_files = [
    ROOT / "frontend" / "src" / "lib" / "integrationConnectionHub.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "integration-connection-hub-status" / "route.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "admin-integration-connection-hub-status" / "route.ts",
]

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

lib_text = required_files[0].read_text(encoding="utf-8")

required_markers = [
    "integration_hub_enabled",
    "client_safe_visibility",
    "admin_governance_visibility",
    "credential_values_exposed: false",
    "external_actions_performed: false",
    "tenant_isolation_enforced",
    "owner_approval_required_for_sensitive_actions",
    "email",
    "crm",
    "calendar",
    "store",
    "website_cms",
    "sms",
    "social",
    "ads",
    "analytics",
    "getClientSafeIntegrationConnectionHubStatus",
]

for marker in required_markers:
    if marker not in lib_text:
        raise AssertionError(f"Missing integration connection hub marker: {marker}")

if re.search(r"credential_values_exposed:\s*true", lib_text):
    raise AssertionError("Credential exposure violation found")

if re.search(r"external_action_performed:\s*true", lib_text):
    raise AssertionError("External action execution violation found")

client_route = required_files[1].read_text(encoding="utf-8")
admin_route = required_files[2].read_text(encoding="utf-8")

if "getClientSafeIntegrationConnectionHubStatus" not in client_route:
    raise AssertionError("Client route must use client-safe integration hub status")

if "getIntegrationConnectionHubStatus" not in admin_route:
    raise AssertionError("Admin route must use full integration hub status")

print("ROW18_INTEGRATION_CONNECTION_HUB_PASSED")
