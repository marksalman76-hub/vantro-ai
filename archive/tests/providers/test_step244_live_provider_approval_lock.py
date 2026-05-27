import json
import os
import urllib.request
from pathlib import Path

ROOT = Path.cwd()
ENV_FILES = [ROOT / ".env.local", ROOT / ".env"]

for env_file in ENV_FILES:
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            clean = line.strip()
            if not clean or clean.startswith("#") or "=" not in clean:
                continue
            key, value = clean.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

record_path = ROOT / "backend" / "app" / "data" / "step244_live_provider_approval_lock.json"
record = json.loads(record_path.read_text(encoding="utf-8"))


def get_json(path):
    req = urllib.request.Request(
        "http://127.0.0.1:8000" + path,
        headers={
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.status, json.loads(res.read().decode("utf-8"))


provider_status, provider = get_json("/admin/provider-readiness")
sdk_status, sdk = get_json("/admin/openai-sdk-readiness")
dashboard_status, dashboard = get_json("/admin/live-llm-readiness-dashboard")
control_status, control = get_json("/admin/live-llm-control")

combined = json.dumps({
    "record": record,
    "provider": provider,
    "sdk": sdk,
    "dashboard": dashboard,
    "control": control,
}).lower()

openai_key_present = bool(os.getenv("OPENAI_API_KEY"))
live_env_enabled = (os.getenv("ENABLE_LIVE_LLM_CALLS") or "").strip().lower() == "true"

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "live_provider_approval_gate_locked",
    "provider_route_ok": provider_status == 200 and provider.get("success") is True,
    "sdk_route_ok": sdk_status == 200 and sdk.get("success") is True,
    "dashboard_route_ok": dashboard_status == 200 and dashboard.get("success") is True,
    "control_route_ok": control_status == 200 and control.get("success") is True,
    "openai_supported": record.get("provider_gate", {}).get("openai_supported") is True,
    "live_gate_required": record.get("provider_gate", {}).get("enable_live_llm_calls_required") is True,
    "owner_control_required": record.get("provider_gate", {}).get("owner_live_control_required") is True,
    "secret_values_not_exposed": all(secret not in combined for secret in [
        "sk_live_",
        "sk_test_",
        "sk-",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
    "openai_key_optional_until_approved": True,
    "live_env_optional_until_approved": True,
}

print("STEP_244_LIVE_PROVIDER_APPROVAL_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

print("provider_env_presence_only", {
    "OPENAI_API_KEY": openai_key_present,
    "ENABLE_LIVE_LLM_CALLS_TRUE": live_env_enabled,
})

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_244_LIVE_PROVIDER_APPROVAL_LOCK_OK")
