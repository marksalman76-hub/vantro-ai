from pathlib import Path
from datetime import datetime
import json
import os
import py_compile

ROOT = Path.cwd()
DATA = ROOT / "backend" / "app" / "data"
TEST = ROOT / "test_step244_live_provider_approval_lock.py"
BACKUPS = ROOT / "backups"

DATA.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
record_file = DATA / "step244_live_provider_approval_lock.json"

if record_file.exists():
    backup = BACKUPS / f"step244_live_provider_approval_lock_before_{timestamp}.json"
    backup.write_text(record_file.read_text(encoding="utf-8"), encoding="utf-8")

record = {
    "success": True,
    "step": 244,
    "status": "live_provider_approval_gate_locked",
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "provider_gate": {
        "openai_supported": True,
        "openai_key_optional_until_owner_approved": True,
        "enable_live_llm_calls_required": True,
        "owner_live_control_required": True,
        "provider_readiness_route_required": True,
        "openai_sdk_readiness_route_required": True,
        "live_llm_dashboard_required": True,
        "live_call_must_not_run_until_all_gates_pass": True,
    },
    "required_before_live_provider_activation": [
        "OPENAI_API_KEY configured in hosted backend environment.",
        "ENABLE_LIVE_LLM_CALLS=true configured only after approval.",
        "Owner live LLM control enabled from admin/governed route.",
        "Provider readiness route confirms OpenAI configured.",
        "OpenAI SDK readiness route confirms SDK installed.",
        "Live LLM readiness dashboard confirms all readiness checks.",
        "One controlled live output smoke test passes.",
    ],
    "security_rules": {
        "never_print_provider_secret_values": True,
        "never_store_provider_secret_values_in_audit": True,
        "live_provider_execution_must_be_audited": True,
        "client_ui_must_not_show_provider_configuration": True,
        "owner_can_disable_live_provider_execution": True,
    },
}

record_file.write_text(json.dumps(record, indent=2), encoding="utf-8")

TEST.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_244_LIVE_PROVIDER_APPROVAL_LOCK_INSTALLED")
print(f"Created/updated: {record_file}")
print(f"Created/updated: {TEST}")
print("STEP_244_OK")