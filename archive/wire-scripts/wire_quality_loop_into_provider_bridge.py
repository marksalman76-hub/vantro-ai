from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

provider_file = ROOT / "backend" / "app" / "runtime" / "provider_connector_registry.py"
test_file = ROOT / "test_quality_loop_provider_bridge.py"

if not provider_file.exists():
    raise FileNotFoundError(f"Missing provider connector registry: {provider_file}")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"provider_connector_registry_before_quality_loop_{timestamp}.py"
source = provider_file.read_text(encoding="utf-8")
backup.write_text(source, encoding="utf-8")

import_block = """from backend.app.runtime.provider_result_quality_loop import (
    apply_quality_loop_to_provider_result,
    decide_retry_from_quality,
)
"""

if import_block not in source:
    lines = source.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, import_block.rstrip())
    source = "\n".join(lines) + "\n"

helper_marker = "# --- Provider result quality loop bridge ---"

helper_block = r'''

# --- Provider result quality loop bridge ---

def _with_provider_quality_loop(result, task_type=None, minimum_score=72):
    try:
        quality_result = apply_quality_loop_to_provider_result(
            result,
            task_type=task_type or result.get("action_type"),
            minimum_score=minimum_score,
        )
        retry_decision = decide_retry_from_quality(
            quality_result,
            retry_count=int(result.get("retry_count", 0) or 0),
            max_retries=int(result.get("max_retries", 3) or 3),
        )
        quality_result["quality_retry_decision"] = retry_decision
        return quality_result
    except Exception as exc:
        safe_result = dict(result)
        safe_result.update(
            {
                "quality_loop_applied": False,
                "quality_loop_error": str(exc)[:500],
                "quality_gate_passed": False,
                "finalisation_status": "requires_manual_review",
                "governance_preserved": True,
                "owner_approval_controls_preserved": True,
            }
        )
        return safe_result
'''

if helper_marker not in source:
    source = source.rstrip() + helper_block + "\n"

old_missing = '''        return {
            "success": True,
            "status": "provider_action_ready",
            "execution_status": "provider_connector_ready",
            "provider_execution_attempted": False,
            "real_provider_configured": False,
            "provider_key": "openai",
            "display_name": "OpenAI",
            "category": "llm",
            "capability": "text",
            "action_type": action_type,
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "payload_received": bool(payload),
            "payload_keys": sorted(list((payload or {}).keys())),
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
            "client_secret_exposure": False,
            "next_stage": "configure_OPENAI_API_KEY_for_live_provider_execution",
            "generated_at": utc_now_iso(),
        }
'''

new_missing = '''        return _with_provider_quality_loop({
            "success": True,
            "status": "provider_action_ready",
            "execution_status": "provider_connector_ready",
            "provider_execution_attempted": False,
            "real_provider_configured": False,
            "provider_key": "openai",
            "display_name": "OpenAI",
            "category": "llm",
            "capability": "text",
            "action_type": action_type,
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "payload_received": bool(payload),
            "payload_keys": sorted(list((payload or {}).keys())),
            "output_text": "Provider connector is ready. Configure OPENAI_API_KEY for live premium output generation.",
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
            "client_secret_exposure": False,
            "next_stage": "configure_OPENAI_API_KEY_for_live_provider_execution",
            "generated_at": utc_now_iso(),
        }, task_type=action_type)
'''

old_success = '''        return {
            "success": True,
            "status": "provider_execution_completed",
            "execution_status": "completed",
            "provider_execution_attempted": True,
            "real_provider_configured": True,
            "provider_key": "openai",
            "display_name": "OpenAI",
            "category": "llm",
            "capability": "text",
            "model": model,
            "action_type": action_type,
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "output_text": output_text.strip(),
            "raw_provider_id": data.get("id"),
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
            "client_secret_exposure": False,
            "generated_at": utc_now_iso(),
        }
'''

new_success = '''        return _with_provider_quality_loop({
            "success": True,
            "status": "provider_execution_completed",
            "execution_status": "completed",
            "provider_execution_attempted": True,
            "real_provider_configured": True,
            "provider_key": "openai",
            "display_name": "OpenAI",
            "category": "llm",
            "capability": "text",
            "model": model,
            "action_type": action_type,
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "output_text": output_text.strip(),
            "raw_provider_id": data.get("id"),
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
            "client_secret_exposure": False,
            "generated_at": utc_now_iso(),
        }, task_type=action_type)
'''

if old_missing not in source:
    raise RuntimeError("Could not find OpenAI missing-key fallback block.")
source = source.replace(old_missing, new_missing, 1)

if old_success not in source:
    raise RuntimeError("Could not find OpenAI provider success block.")
source = source.replace(old_success, new_success, 1)

# Wire generic non-OpenAI ready result into the quality loop too.
old_generic = '''    return {
        "success": True,
        "status": "provider_action_ready",
        "execution_status": "provider_connector_ready",
        "provider_execution_attempted": False,
        "real_provider_configured": configured,
        "provider_key": connector.provider_key,
        "display_name": connector.display_name,
        "category": connector.category,
        "capability": capability,
        "action_type": action_type,
        "tenant_id": tenant_id,
        "actor_role": actor_role,
        "payload_received": bool(payload),
        "payload_keys": sorted(list(payload.keys())),
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
        "client_secret_exposure": False,
        "next_stage": "wire_real_provider_api_call_when_key_configured",
        "generated_at": utc_now_iso(),
    }
'''

new_generic = '''    return _with_provider_quality_loop({
        "success": True,
        "status": "provider_action_ready",
        "execution_status": "provider_connector_ready",
        "provider_execution_attempted": False,
        "real_provider_configured": configured,
        "provider_key": connector.provider_key,
        "display_name": connector.display_name,
        "category": connector.category,
        "capability": capability,
        "action_type": action_type,
        "tenant_id": tenant_id,
        "actor_role": actor_role,
        "payload_received": bool(payload),
        "payload_keys": sorted(list(payload.keys())),
        "output_text": "Provider connector is ready. Configure the provider API key for live premium output generation.",
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
        "client_secret_exposure": False,
        "next_stage": "wire_real_provider_api_call_when_key_configured",
        "generated_at": utc_now_iso(),
    }, task_type=action_type)
'''

if old_generic not in source:
    raise RuntimeError("Could not find generic provider_action_ready return block.")
source = source.replace(old_generic, new_generic, 1)

provider_file.write_text(source, encoding="utf-8")

test_file.write_text(r'''
import os

from backend.app.runtime.execution_stack import execute_safe_generation_via_provider_bridge
from backend.app.runtime.provider_connector_registry import execute_provider_action


def main():
    original_key = os.environ.pop("OPENAI_API_KEY", None)

    try:
        openai_ready = execute_provider_action(
            provider_key="openai",
            action_type="marketing_campaign_execution",
            payload={"business": "Quality bridge test", "goal": "Verify quality loop"},
            capability="text",
            tenant_id="owner_admin_test",
            actor_role="owner_admin",
        )

        runtime_ready = execute_safe_generation_via_provider_bridge(
            action_type="marketing_campaign_execution",
            payload={"business": "Runtime quality bridge", "goal": "Verify runtime quality loop"},
            tenant_id="owner_admin_test",
            actor_role="owner_admin",
            preferred_provider="openai",
        )

        image_ready = execute_provider_action(
            provider_key="image_provider",
            action_type="image_generation",
            payload={"brief": "Premium product image"},
            capability="image",
            tenant_id="owner_admin_test",
            actor_role="owner_admin",
        )

        blocked = execute_safe_generation_via_provider_bridge(
            action_type="scale_campaign",
            payload={"budget_increase": 1000},
            tenant_id="client_test",
            actor_role="customer",
            preferred_provider="openai",
        )

        print("QUALITY_LOOP_PROVIDER_BRIDGE_TEST")
        print("openai_status", openai_ready["status"])
        print("openai_quality_loop", openai_ready.get("quality_loop_applied"))
        print("openai_quality_status", openai_ready.get("quality", {}).get("status"))
        print("openai_finalisation", openai_ready.get("finalisation_status"))
        print("openai_retry_decision", openai_ready.get("quality_retry_decision", {}).get("decision"))
        print("runtime_bridge_status", runtime_ready.get("runtime_bridge_status"))
        print("runtime_quality_loop", runtime_ready.get("quality_loop_applied"))
        print("image_quality_loop", image_ready.get("quality_loop_applied"))
        print("image_finalisation", image_ready.get("finalisation_status"))
        print("blocked_status", blocked["status"])
        print("blocked_attempted", blocked["provider_execution_attempted"])
        print("governance", runtime_ready["governance_preserved"])

        assert openai_ready["success"] is True
        assert openai_ready["status"] == "provider_action_ready"
        assert openai_ready["quality_loop_applied"] is True
        assert "quality" in openai_ready
        assert "quality_retry_decision" in openai_ready
        assert openai_ready["client_secret_exposure"] is False

        assert runtime_ready["success"] is True
        assert runtime_ready["runtime_bridge_status"] == "provider_registry_routed"
        assert runtime_ready["quality_loop_applied"] is True
        assert runtime_ready["governance_preserved"] is True

        assert image_ready["success"] is True
        assert image_ready["quality_loop_applied"] is True
        assert "quality" in image_ready

        assert blocked["success"] is False
        assert blocked["status"] == "owner_approval_required"
        assert blocked["provider_execution_attempted"] is False

        print("QUALITY_LOOP_PROVIDER_BRIDGE_OK")

    finally:
        if original_key is not None:
            os.environ["OPENAI_API_KEY"] = original_key


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

print("QUALITY_LOOP_PROVIDER_BRIDGE_WIRED")
print(f"Backup: {backup}")
print(f"Updated: {provider_file}")
print(f"Created/updated: {test_file}")
print("Provider results now receive quality scoring and retry/manual-review guidance.")