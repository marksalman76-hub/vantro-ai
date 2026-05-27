from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

provider_file = ROOT / "backend" / "app" / "runtime" / "provider_connector_registry.py"
test_file = ROOT / "test_real_openai_provider_execution_path.py"

if not provider_file.exists():
    raise FileNotFoundError(f"Missing provider registry: {provider_file}")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"provider_connector_registry_before_real_openai_{timestamp}.py"
source = provider_file.read_text(encoding="utf-8")
backup.write_text(source, encoding="utf-8")

real_openai_block = r'''

# --- Real OpenAI provider execution path ---
# Safe-by-default. No API call is attempted unless OPENAI_API_KEY is configured.

def _safe_openai_text_execution(action_type, payload, tenant_id=None, actor_role="system"):
    import json
    import os
    import urllib.request
    import urllib.error

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return {
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

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini"

    business = payload.get("business") or payload.get("brand") or payload.get("company") or "the client business"
    goal = payload.get("goal") or payload.get("task") or payload.get("brief") or "produce a premium ecommerce execution output"

    prompt = (
        "You are operating inside a governed ecommerce AI workforce platform. "
        "Produce a concise, premium, commercially useful output. "
        "Do not claim to spend money, publish, scale campaigns, sign contracts, or perform external actions. "
        f"Business/context: {business}. "
        f"Goal/task: {goal}. "
        f"Input payload: {json.dumps(payload, ensure_ascii=False)[:4000]}"
    )

    request_payload = {
        "model": model,
        "input": prompt,
        "max_output_tokens": 900,
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(request_payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)

        output_text = ""
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    output_text += content.get("text", "")

        return {
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

    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")[:1200]
        return {
            "success": False,
            "status": "provider_execution_failed",
            "execution_status": "failed",
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
            "http_status": exc.code,
            "error": error_body,
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
            "client_secret_exposure": False,
            "generated_at": utc_now_iso(),
        }

    except Exception as exc:
        return {
            "success": False,
            "status": "provider_execution_failed",
            "execution_status": "failed",
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
            "error": str(exc)[:1200],
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
            "client_secret_exposure": False,
            "generated_at": utc_now_iso(),
        }
'''

if "# --- Real OpenAI provider execution path ---" not in source:
    source = source.rstrip() + real_openai_block + "\n"

old = '''    configured = provider_available(connector.provider_key)

    return {
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

new = '''    configured = provider_available(connector.provider_key)

    if connector.provider_key == "openai" and capability == "text":
        return _safe_openai_text_execution(
            action_type=action_type,
            payload=payload,
            tenant_id=tenant_id,
            actor_role=actor_role,
        )

    return {
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

if old not in source:
    raise RuntimeError("Could not find expected provider_action_ready return block. No changes written.")

source = source.replace(old, new, 1)
provider_file.write_text(source, encoding="utf-8")

test_file.write_text(r'''
import os

from backend.app.runtime.execution_stack import execute_safe_generation_via_provider_bridge
from backend.app.runtime.provider_connector_registry import execute_provider_action


def main():
    original_key = os.environ.pop("OPENAI_API_KEY", None)

    try:
        missing_key = execute_provider_action(
            provider_key="openai",
            action_type="marketing_campaign_execution",
            payload={"business": "Missing key test", "goal": "Verify safe fallback"},
            capability="text",
            tenant_id="owner_admin_test",
            actor_role="owner_admin",
        )

        runtime_missing_key = execute_safe_generation_via_provider_bridge(
            action_type="marketing_campaign_execution",
            payload={"business": "Runtime missing key test", "goal": "Verify bridge fallback"},
            tenant_id="owner_admin_test",
            actor_role="owner_admin",
            preferred_provider="openai",
        )

        blocked = execute_safe_generation_via_provider_bridge(
            action_type="scale_campaign",
            payload={"budget_increase": 1000},
            tenant_id="client_test",
            actor_role="customer",
            preferred_provider="openai",
        )

        print("REAL_OPENAI_PROVIDER_EXECUTION_PATH_TEST")
        print("missing_key_status", missing_key["status"])
        print("missing_key_attempted", missing_key["provider_execution_attempted"])
        print("missing_key_configured", missing_key["real_provider_configured"])
        print("missing_key_secret_exposure", missing_key["client_secret_exposure"])
        print("runtime_status", runtime_missing_key["status"])
        print("runtime_bridge_status", runtime_missing_key.get("runtime_bridge_status"))
        print("runtime_attempted", runtime_missing_key["provider_execution_attempted"])
        print("blocked_status", blocked["status"])
        print("blocked_execution", blocked["execution_status"])
        print("blocked_attempted", blocked["provider_execution_attempted"])

        assert missing_key["success"] is True
        assert missing_key["status"] == "provider_action_ready"
        assert missing_key["provider_execution_attempted"] is False
        assert missing_key["real_provider_configured"] is False
        assert missing_key["client_secret_exposure"] is False

        assert runtime_missing_key["success"] is True
        assert runtime_missing_key["status"] == "provider_action_ready"
        assert runtime_missing_key["runtime_bridge_status"] == "provider_registry_routed"
        assert runtime_missing_key["provider_execution_attempted"] is False

        assert blocked["success"] is False
        assert blocked["status"] == "owner_approval_required"
        assert blocked["provider_execution_attempted"] is False

        print("REAL_OPENAI_PROVIDER_EXECUTION_PATH_OK")

    finally:
        if original_key is not None:
            os.environ["OPENAI_API_KEY"] = original_key


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

print("REAL_OPENAI_PROVIDER_EXECUTION_PATH_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {provider_file}")
print(f"Created/updated: {test_file}")
print("OpenAI text execution path added with safe fallback when OPENAI_API_KEY is missing.")