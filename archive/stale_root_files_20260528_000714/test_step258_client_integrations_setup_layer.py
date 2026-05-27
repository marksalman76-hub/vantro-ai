import json
from pathlib import Path

ROOT = Path.cwd()
record = json.loads((ROOT / "backend" / "app" / "data" / "step258_client_integrations_setup_layer.json").read_text(encoding="utf-8"))
doc = ROOT / "docs" / "operations" / "client-integrations-setup.md"

required = ["shopify", "crm", "email_marketing", "ads", "analytics", "support"]

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "client_integrations_setup_layer_locked",
    "portal_only_mode_present": "portal_only_mode" in record.get("usage_modes", {}),
    "connected_execution_mode_present": "connected_execution_mode" in record.get("usage_modes", {}),
    "all_integration_categories_present": all(key in record.get("integration_categories", {}) for key in required),
    "onboarding_flow_present": len(record.get("onboarding_flow", [])) >= 6,
    "setup_doc_created": doc.exists(),
}

print("STEP_258_CLIENT_INTEGRATIONS_SETUP_LAYER_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]
if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_258_CLIENT_INTEGRATIONS_SETUP_LAYER_OK")
