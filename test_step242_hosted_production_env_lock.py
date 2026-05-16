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
