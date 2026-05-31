from pathlib import Path
import json
import os

ROOT = Path.cwd()
manifest = json.loads((ROOT / "config" / "security" / "production-secret-manifest.json").read_text(encoding="utf-8"))

required = manifest["required_secrets"]
inventory = {}
missing = []

for name in required:
    value = os.getenv(name)
    inventory[name] = {
        "present": bool(value),
        "masked": "" if not value else value[:3] + "..." + value[-3:] if len(value) > 8 else "***",
        "source": "environment",
    }
    if not value:
        missing.append(name)

report = {
    "success": len(missing) == 0,
    "mode": "production_env_validator",
    "secret_values_exposed": False,
    "missing": missing,
    "present_count": len(required) - len(missing),
    "required_count": len(required),
    "inventory": inventory,
}

out = ROOT / "telemetry" / "security" / "production-env-validator.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("PRODUCTION_ENV_VALIDATOR_COMPLETED")
print("SECRET_VALUES_EXPOSED:false")
print("PRESENT_COUNT:", report["present_count"])
print("MISSING_COUNT:", len(missing))

if missing:
    print("PRODUCTION_ENV_NOT_READY_OWNER_SECRET_SETUP_REQUIRED")
