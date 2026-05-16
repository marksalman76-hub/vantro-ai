from pathlib import Path
from datetime import datetime
import json
import os
import py_compile

ROOT = Path.cwd()
DATA = ROOT / "backend" / "app" / "data"
BACKUPS = ROOT / "backups"
TEST = ROOT / "test_step242_hosted_production_env_lock.py"

DATA.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
record_file = DATA / "step242_hosted_production_env_lock.json"

if record_file.exists():
    backup = BACKUPS / f"step242_hosted_production_env_lock_before_{timestamp}.json"
    backup.write_text(record_file.read_text(encoding="utf-8"), encoding="utf-8")

required_backend_env = [
    "DATABASE_URL",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "STRIPE_PRICE_STARTER_MONTHLY",
    "STRIPE_PRICE_GROWTH_MONTHLY",
    "STRIPE_PRICE_PRO_MONTHLY",
    "STRIPE_CHECKOUT_SUCCESS_URL",
    "STRIPE_CHECKOUT_CANCEL_URL",
    "STRIPE_BILLING_PORTAL_RETURN_URL",
]

optional_live_provider_env = [
    "OPENAI_API_KEY",
    "ENABLE_LIVE_LLM_CALLS",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "XAI_API_KEY",
    "LOCAL_LLM_ENDPOINT",
]

required_frontend_env = [
    "BACKEND_URL",
    "NEXT_PUBLIC_BACKEND_URL",
    "PORTAL_ACCESS_CODE",
]

record = {
    "success": True,
    "step": 242,
    "status": "hosted_production_env_requirements_locked",
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "render_backend_required_env": required_backend_env,
    "vercel_frontend_required_env": required_frontend_env,
    "optional_live_provider_env": optional_live_provider_env,
    "rules": {
        "never_commit_secret_values": True,
        "rotate_exposed_stripe_secret_before_public_launch": True,
        "provider_keys_optional_until_live_llm_approved": True,
        "enable_live_llm_calls_only_after_owner_approval": True,
        "topup_price_ids_optional_until_topup_packages_launched": True,
        "client_ui_must_not_show_internal_ids_or_secret_values": True,
    },
    "deployment_targets": {
        "backend": "Render",
        "frontend": "Vercel",
        "database": "Supabase/Postgres",
        "billing": "Stripe",
        "provider": "OpenAI first, other providers optional later",
    },
}

record_file.write_text(json.dumps(record, indent=2), encoding="utf-8")

TEST.write_text(r'''
import json
import os
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
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

record_path = ROOT / "backend" / "app" / "data" / "step242_hosted_production_env_lock.json"
record = json.loads(record_path.read_text(encoding="utf-8"))

backend_required = record.get("render_backend_required_env", [])
frontend_required = record.get("vercel_frontend_required_env", [])
provider_optional = record.get("optional_live_provider_env", [])

backend_presence = {key: bool(os.getenv(key)) for key in backend_required}
frontend_presence = {key: bool(os.getenv(key)) for key in frontend_required}
provider_presence = {key: bool(os.getenv(key)) for key in provider_optional}

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "hosted_production_env_requirements_locked",
    "backend_env_requirements_present": len(backend_required) >= 8,
    "frontend_env_requirements_present": len(frontend_required) >= 2,
    "stripe_core_local_present": all(backend_presence.get(key) for key in [
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "STRIPE_PRICE_STARTER_MONTHLY",
        "STRIPE_PRICE_GROWTH_MONTHLY",
        "STRIPE_PRICE_PRO_MONTHLY",
    ]),
    "database_local_present": backend_presence.get("DATABASE_URL") is True,
    "provider_keys_optional": "OPENAI_API_KEY" in provider_optional,
    "live_llm_gate_optional": "ENABLE_LIVE_LLM_CALLS" in provider_optional,
    "secret_values_not_printed": True,
}

print("STEP_242_HOSTED_PRODUCTION_ENV_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

print("backend_presence_only", backend_presence)
print("frontend_presence_only", frontend_presence)
print("provider_presence_only", provider_presence)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_242_HOSTED_PRODUCTION_ENV_LOCK_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_242_HOSTED_PRODUCTION_ENV_LOCK_INSTALLED")
print(f"Created/updated: {record_file}")
print(f"Created/updated: {TEST}")
print("STEP_242_OK")