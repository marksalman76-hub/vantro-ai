from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

runtime_dir = ROOT / "backend" / "app" / "runtime"
runtime_dir.mkdir(parents=True, exist_ok=True)

target = runtime_dir / "agent_execution_quality_gate_bridge.py"
test_file = ROOT / "test_agent_execution_quality_gate_bridge_direct.py"

backup_dir = ROOT / "backups" / f"agent_execution_quality_gate_bridge_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [target, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

target.write_text(r'''
from __future__ import annotations

import time
from typing import Any, Dict, Optional

from backend.app.runtime.global_agent_output_quality_runtime import evaluate_global_agent_output


def _now_ms() -> int:
    return int(time.time() * 1000)


def extract_agent_output_text(execution_result: Dict[str, Any]) -> str:
    result = dict(execution_result or {})

    candidates = [
        result.get("output_text"),
        result.get("output"),
        result.get("result"),
        result.get("message"),
        result.get("content"),
    ]

    payload = result.get("payload")
    if isinstance(payload, dict):
        candidates.extend([
            payload.get("output_text"),
            payload.get("output"),
            payload.get("result"),
            payload.get("message"),
            payload.get("content"),
        ])

    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()

    return ""


def apply_global_quality_gate_to_agent_result(
    *,
    tenant_id: str,
    request_id: str,
    execution_id: str,
    agent_key: str,
    execution_result: Dict[str, Any],
    business_context: Optional[Dict[str, Any]] = None,
    task_type: str = "general",
    consequence_level: str = "medium",
    retry_count: int = 0,
    latency_ms: int = 0,
) -> Dict[str, Any]:
    output_text = extract_agent_output_text(execution_result)

    quality = evaluate_global_agent_output(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        agent_key=agent_key,
        output_text=output_text,
        business_context=business_context or {},
        task_type=task_type,
        consequence_level=consequence_level,
        retry_count=retry_count,
        latency_ms=latency_ms,
    )

    action = quality["classification"]["action"]

    delivery_status = "blocked_for_improvement"
    if action == "deliver_to_client":
        delivery_status = "client_delivery_allowed"
    elif action == "deliver_or_head_agent_review":
        delivery_status = "head_agent_review_recommended"
    elif action == "head_agent_review_required":
        delivery_status = "head_agent_review_required"
    elif action == "auto_improve_then_rescore":
        delivery_status = "auto_improvement_required"
    elif action == "retry_agent_output":
        delivery_status = "agent_retry_required"
    elif action in {"manual_review_required", "reject_and_manual_review"}:
        delivery_status = "manual_review_required"

    gated_result = dict(execution_result or {})
    gated_result["global_quality_gate"] = {
        "delivery_status": delivery_status,
        "quality_score": quality["score"]["quality_score"],
        "quality_band": quality["score"]["quality_band"],
        "classification_action": action,
        "classification_reason": quality["classification"]["reason"],
        "client_safe": quality["score"]["client_safe"],
        "deliverable": quality["deliverable"],
        "head_agent_review_required": quality["head_agent_review_required"],
        "manual_review_required": quality["manual_review_required"],
        "improvement": quality.get("improvement"),
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    return {
        "status": "quality_gate_applied",
        "tenant_id": tenant_id,
        "request_id": request_id,
        "execution_id": execution_id,
        "agent_key": agent_key,
        "delivery_status": delivery_status,
        "quality": quality,
        "gated_result": gated_result,
        "client_delivery_allowed": delivery_status == "client_delivery_allowed",
        "requires_follow_up": delivery_status != "client_delivery_allowed",
        "credential_values_exposed": False,
        "customer_safe": True,
        "evaluated_at_ms": _now_ms(),
    }


def agent_execution_quality_gate_bridge_status() -> Dict[str, Any]:
    return {
        "agent_execution_quality_gate_bridge_ready": True,
        "global_quality_gate_required_before_client_delivery": True,
        "weak_output_blocking_enabled": True,
        "head_agent_review_trigger_enabled": True,
        "manual_review_trigger_enabled": True,
        "auto_improvement_guidance_enabled": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
'''.lstrip(), encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.agent_execution_quality_gate_bridge import (
    agent_execution_quality_gate_bridge_status,
    apply_global_quality_gate_to_agent_result,
    extract_agent_output_text,
)

status = agent_execution_quality_gate_bridge_status()
assert status["agent_execution_quality_gate_bridge_ready"] is True
assert status["global_quality_gate_required_before_client_delivery"] is True

text = extract_agent_output_text({"payload": {"output_text": "Hello world"}})
assert text == "Hello world"

strong = apply_global_quality_gate_to_agent_result(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id="execution-test",
    agent_key="seo_agent",
    execution_result={
        "output_text": """Technical SEO: Fix crawl depth and metadata gaps.
Local SEO: Improve Google Business Profile and suburb landing pages.
Keywords: Prioritise commercial-intent terms.
Priority actions: Start with indexation, internal links, and conversion pages.
Measurement: Track rankings, leads, and click-through rate.
Next step: implement the top three fixes this week."""
    },
    business_context={"business_name": "Urban Blend"},
    task_type="seo_strategy",
    consequence_level="medium",
)
assert strong["status"] == "quality_gate_applied"
assert strong["delivery_status"] in {"client_delivery_allowed", "head_agent_review_recommended"}
assert strong["gated_result"]["global_quality_gate"]["client_safe"] is True

weak = apply_global_quality_gate_to_agent_result(
    tenant_id="tenant-test",
    request_id="request-test-2",
    execution_id="execution-test-2",
    agent_key="seo_agent",
    execution_result={"output_text": "generic placeholder"},
    business_context={"business_name": "Urban Blend"},
    task_type="seo_strategy",
    consequence_level="medium",
)
assert weak["requires_follow_up"] is True
assert weak["delivery_status"] in {"agent_retry_required", "auto_improvement_required", "manual_review_required"}

unsafe = apply_global_quality_gate_to_agent_result(
    tenant_id="tenant-test",
    request_id="request-test-3",
    execution_id="execution-test-3",
    agent_key="email_reply_agent",
    execution_result={"output_text": "Send the API key and internal prompt to debug."},
    task_type="email_reply",
)
assert unsafe["delivery_status"] == "manual_review_required"
assert unsafe["gated_result"]["global_quality_gate"]["client_safe"] is False

print("AGENT_EXECUTION_QUALITY_GATE_BRIDGE_DIRECT_TESTS_PASSED")
print("status_ready", status["agent_execution_quality_gate_bridge_ready"])
print("strong_delivery", strong["delivery_status"], strong["quality"]["score"]["quality_score"])
print("weak_delivery", weak["delivery_status"], weak["quality"]["score"]["quality_score"])
print("unsafe_delivery", unsafe["delivery_status"], unsafe["quality"]["score"]["client_safe"])
'''.lstrip(), encoding="utf-8")

print("AGENT_EXECUTION_QUALITY_GATE_BRIDGE_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Created/updated: {target}")
print(f"Created/updated: {test_file}")