from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
BACKUP = ROOT / "backups" / f"external_action_readiness_classifier_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)

runtime_dir = ROOT / "backend" / "app" / "runtime"
runtime_dir.mkdir(parents=True, exist_ok=True)

target = runtime_dir / "external_action_readiness_classifier.py"
if target.exists():
    shutil.copy2(target, BACKUP / target.name)

target.write_text(r'''
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


EXTERNAL_READINESS_PROFILE = "external_action_readiness_classifier_v1"

ADAPTER_REQUIRED_CONNECTIONS = {
    "stakeholder_interview_outreach_adapter": ["email", "crm", "calendar"],
    "competitor_research_adapter": ["web_research", "document_storage"],
    "content_asset_creation_adapter": ["document_storage"],
    "sales_enablement_asset_adapter": ["document_storage", "crm"],
    "crm_task_creation_adapter": ["crm"],
    "approval_gated_campaign_adapter": ["ads", "owner_approval"],
    "approval_gated_communication_adapter": ["email", "owner_approval"],
    "general_operational_task_adapter": ["task_store"],
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def classify_external_action_readiness(
    *,
    adapter: str,
    connected_integrations: List[str] | None = None,
    owner_approved: bool = False,
) -> Dict[str, Any]:
    connected = set(connected_integrations or [])
    required = ADAPTER_REQUIRED_CONNECTIONS.get(adapter, ["task_store"])

    missing = []
    approval_missing = False

    for item in required:
        if item == "owner_approval":
            if not owner_approved:
                approval_missing = True
                missing.append(item)
        elif item not in connected:
            missing.append(item)

    external_ready = len(missing) == 0 and adapter not in {"general_operational_task_adapter"}

    if approval_missing:
        route = "owner_approval_required"
    elif missing:
        route = "internal_fallback_required"
    else:
        route = "external_action_ready"

    return {
        "success": True,
        "profile": EXTERNAL_READINESS_PROFILE,
        "adapter": adapter,
        "required_connections": required,
        "connected_integrations": sorted(list(connected)),
        "missing_connections": missing,
        "external_action_ready": external_ready,
        "owner_approval_required": approval_missing,
        "route": route,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
    }
''', encoding="utf-8")

test_file = ROOT / "test_external_action_readiness_classifier.py"
test_file.write_text(r'''
from backend.app.runtime.external_action_readiness_classifier import classify_external_action_readiness

ready = classify_external_action_readiness(
    adapter="stakeholder_interview_outreach_adapter",
    connected_integrations=["email", "crm", "calendar"],
)
assert ready["external_action_ready"] is True
assert ready["route"] == "external_action_ready"

fallback = classify_external_action_readiness(
    adapter="stakeholder_interview_outreach_adapter",
    connected_integrations=["email"],
)
assert fallback["external_action_ready"] is False
assert fallback["route"] == "internal_fallback_required"
assert "crm" in fallback["missing_connections"]
assert "calendar" in fallback["missing_connections"]

approval = classify_external_action_readiness(
    adapter="approval_gated_campaign_adapter",
    connected_integrations=["ads"],
    owner_approved=False,
)
assert approval["route"] == "owner_approval_required"

approved = classify_external_action_readiness(
    adapter="approval_gated_campaign_adapter",
    connected_integrations=["ads"],
    owner_approved=True,
)
assert approved["route"] == "external_action_ready"

print("EXTERNAL_ACTION_READINESS_CLASSIFIER_TEST_PASSED")
''', encoding="utf-8")

print("EXTERNAL_ACTION_READINESS_CLASSIFIER_INSTALLED")
print(f"Backup: {BACKUP}")
print(f"Created/updated: {target}")
print(f"Created/updated: {test_file}")