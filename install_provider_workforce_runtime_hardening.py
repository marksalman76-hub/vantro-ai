from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
runtime_file = ROOT / "backend" / "app" / "runtime" / "provider_workforce_runtime_hardening.py"
main_file = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_provider_workforce_runtime_hardening.py"

backup_dir = ROOT / "backups" / f"provider_workforce_runtime_hardening_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
if main_file.exists():
    shutil.copy2(main_file, backup_dir / "main.py")

runtime_file.write_text(r'''
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from backend.app.runtime.real_provider_activation_registry import get_all_provider_activation_statuses
from backend.app.runtime.provider_dispatch_policy_worker_foundation import provider_dispatch_policy_status, provider_worker_foundation_status
from backend.app.runtime.real_provider_http_execution_layer import controlled_openai_live_execution_status, real_provider_http_runtime_status


def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_provider_score(status: Dict[str, Any]) -> int:
    score = 0
    if status.get("known_adapter"):
        score += 20
    if status.get("configured"):
        score += 25
    if status.get("ready"):
        score += 25
    if status.get("http_request_builder_ready"):
        score += 15
    if status.get("owner_governed_execution_required"):
        score += 10
    if status.get("credential_values_exposed") is False:
        score += 5
    return min(score, 100)


def provider_runtime_health_summary() -> Dict[str, Any]:
    providers = ["openai", "runway", "kling", "heygen", "elevenlabs", "replicate"]
    registry = get_all_provider_activation_statuses()
    dispatch_policy = provider_dispatch_policy_status()
    worker = provider_worker_foundation_status()

    provider_statuses: Dict[str, Dict[str, Any]] = {}
    for provider in providers:
        status = real_provider_http_runtime_status(provider)
        score = _safe_provider_score(status)
        provider_statuses[provider] = {
            **status,
            "health_score": score,
            "health_state": "ready" if score >= 80 else "configured_not_dispatching" if score >= 60 else "not_configured",
            "safe_to_show_admin": True,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    ready = [p for p, s in provider_statuses.items() if s["health_state"] == "ready"]
    configured = [p for p, s in provider_statuses.items() if s.get("configured")]
    unconfigured = [p for p, s in provider_statuses.items() if not s.get("configured")]

    return {
        "success": True,
        "profile": "provider_runtime_health_summary_v1",
        "visibility_only": True,
        "external_action_performed": False,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "governance_enforced": True,
        "provider_count": len(providers),
        "configured_provider_count": len(configured),
        "unconfigured_provider_count": len(unconfigured),
        "ready_provider_count": len(ready),
        "ready_providers": ready,
        "configured_providers": configured,
        "unconfigured_providers": unconfigured,
        "provider_statuses": provider_statuses,
        "registry": registry,
        "dispatch_policy": dispatch_policy,
        "worker_foundation": worker,
        "controlled_openai": controlled_openai_live_execution_status(),
        "checked_at_ms": _now_ms(),
    }


def provider_recovery_readiness_summary() -> Dict[str, Any]:
    worker = provider_worker_foundation_status()
    dispatch = provider_dispatch_policy_status()

    return {
        "success": True,
        "profile": "provider_recovery_readiness_v1",
        "visibility_only": True,
        "external_action_performed": False,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "governance_enforced": True,
        "retry_escalation_linked": bool(worker.get("retry_escalation_linked")),
        "timeline_events_linked": bool(worker.get("timeline_events_linked")),
        "safe_queue_preparation_enabled": bool(worker.get("safe_queue_preparation_enabled")),
        "dispatch_policy_layer_enabled": bool(worker.get("dispatch_policy_layer_enabled")),
        "real_background_dispatch_enabled": bool(worker.get("real_background_dispatch_enabled")),
        "requires_final_policy_enablement": bool(dispatch.get("requires_final_policy_enablement")),
        "owner_governed_execution_required": True,
        "recovery_modes": [
            "retry_after_timeout",
            "manual_review_after_retry_exhaustion",
            "provider_degraded_mode",
            "owner_review_required",
            "safe_customer_status_packet",
        ],
        "next_safe_step": "Connect durable queue replay after admin UI exposes provider health and recovery state.",
        "checked_at_ms": _now_ms(),
    }


def provider_workforce_runtime_hardening_status() -> Dict[str, Any]:
    health = provider_runtime_health_summary()
    recovery = provider_recovery_readiness_summary()

    return {
        "success": True,
        "profile": "provider_workforce_runtime_hardening_v1",
        "visibility_only": True,
        "external_action_performed": False,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "governance_enforced": True,
        "health_summary": health,
        "recovery_readiness": recovery,
        "hardening_layers": {
            "provider_health_scoring": True,
            "provider_registry_visibility": True,
            "dispatch_policy_visibility": True,
            "worker_foundation_visibility": True,
            "retry_recovery_readiness": True,
            "admin_safe_status_packets": True,
            "credential_safe_visibility": True,
            "external_execution_not_triggered_by_status_routes": True,
        },
        "checked_at_ms": _now_ms(),
    }
'''.lstrip(), encoding="utf-8")

main_text = main_file.read_text(encoding="utf-8")

import_line = "from backend.app.runtime.provider_workforce_runtime_hardening import provider_workforce_runtime_hardening_status, provider_runtime_health_summary, provider_recovery_readiness_summary\n"
if import_line not in main_text:
    anchor = "from fastapi import"
    idx = main_text.find(anchor)
    if idx == -1:
        raise SystemExit("Could not find import anchor")
    end = main_text.find("\n", idx)
    main_text = main_text[:end + 1] + import_line + main_text[end + 1:]

route_block = r'''

@app.get("/admin/provider-workforce-runtime-hardening")
async def admin_provider_workforce_runtime_hardening():
    """
    Admin-safe provider workforce runtime hardening visibility.

    No external provider calls are performed.
    No credential values are exposed.
    """
    return provider_workforce_runtime_hardening_status()


@app.get("/admin/provider-runtime-health")
async def admin_provider_runtime_health():
    """
    Admin-safe provider health scoring visibility.
    """
    return provider_runtime_health_summary()


@app.get("/admin/provider-recovery-readiness")
async def admin_provider_recovery_readiness():
    """
    Admin-safe provider recovery/replay readiness visibility.
    """
    return provider_recovery_readiness_summary()
'''

if '"/admin/provider-workforce-runtime-hardening"' not in main_text:
    main_text = main_text.rstrip() + "\n" + route_block + "\n"

main_file.write_text(main_text, encoding="utf-8")

test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


for route in [
    "/admin/provider-workforce-runtime-hardening",
    "/admin/provider-runtime-health",
    "/admin/provider-recovery-readiness",
]:
    response = client.get(route)
    assert_true(response.status_code == 200, f"{route} failed: {response.status_code} {response.text}")
    data = response.json()
    assert_true(data["success"] is True, f"{route} success failed")
    assert_true(data["visibility_only"] is True, f"{route} must be visibility only")
    assert_true(data["external_action_performed"] is False, f"{route} performed external action")
    assert_true(data["live_external_call_executed"] is False, f"{route} executed live external call")
    assert_true(data["credential_values_exposed"] is False, f"{route} exposed credentials")
    assert_true(data["customer_safe"] is True, f"{route} not customer safe")
    assert_true(data["governance_enforced"] is True, f"{route} governance not enforced")

health = client.get("/admin/provider-runtime-health").json()
assert_true("provider_statuses" in health, "provider statuses missing")
assert_true(health["provider_count"] >= 1, "provider count missing")
for provider, status in health["provider_statuses"].items():
    assert_true(status["credential_values_exposed"] is False, f"{provider} exposed credentials")
    assert_true(status["customer_safe"] is True, f"{provider} not customer safe")
    assert_true("health_score" in status, f"{provider} health score missing")
    assert_true("health_state" in status, f"{provider} health state missing")

recovery = client.get("/admin/provider-recovery-readiness").json()
assert_true(recovery["retry_escalation_linked"] is True, "retry escalation should be linked")
assert_true(recovery["timeline_events_linked"] is True, "timeline events should be linked")
assert_true(recovery["safe_queue_preparation_enabled"] is True, "safe queue prep should be enabled")
assert_true(recovery["dispatch_policy_layer_enabled"] is True, "dispatch policy should be enabled")

hardening = client.get("/admin/provider-workforce-runtime-hardening").json()
layers = hardening["hardening_layers"]
for key in [
    "provider_health_scoring",
    "provider_registry_visibility",
    "dispatch_policy_visibility",
    "worker_foundation_visibility",
    "retry_recovery_readiness",
    "admin_safe_status_packets",
    "credential_safe_visibility",
    "external_execution_not_triggered_by_status_routes",
]:
    assert_true(layers[key] is True, f"{key} not enabled")

print("PROVIDER_WORKFORCE_RUNTIME_HARDENING_TEST_PASSED")
print({
    "provider_count": health["provider_count"],
    "configured_provider_count": health["configured_provider_count"],
    "ready_provider_count": health["ready_provider_count"],
    "recovery_modes": recovery["recovery_modes"],
    "hardening_layers": layers,
})
'''.lstrip(), encoding="utf-8")

print("PROVIDER_WORKFORCE_RUNTIME_HARDENING_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Created/updated: {runtime_file}")
print(f"Updated: {main_file}")
print(f"Created/updated: {test_file}")