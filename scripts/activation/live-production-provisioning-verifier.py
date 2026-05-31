from pathlib import Path
from datetime import datetime
import json
import os

ROOT = Path.cwd()

required = {
    "render_backend": [
        "ADMIN_PLATFORM_TOKEN",
        "JWT_SECRET",
        "SESSION_SECRET",
        "DATABASE_URL",
        "OPENAI_API_KEY",
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "SMTP_PASSWORD",
        "BREVO_API_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
    ],
    "vercel_frontend": [
        "ADMIN_PLATFORM_TOKEN",
        "SESSION_SECRET",
    ],
    "supabase": [
        "DATABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
    ],
}

def masked(name):
    value = os.getenv(name)
    if not value:
        return {"present": False, "masked": ""}
    return {"present": True, "masked": value[:3] + "..." + value[-3:] if len(value) > 8 else "***"}

sections = {}
all_missing = []

for section, names in required.items():
    missing = []
    inventory = {}
    for name in names:
        item = masked(name)
        inventory[name] = item
        if not item["present"]:
            missing.append(name)
            all_missing.append(f"{section}:{name}")

    sections[section] = {
        "ready": len(missing) == 0,
        "missing": missing,
        "inventory": inventory
    }

report = {
    "success": len(all_missing) == 0,
    "mode": "live_production_provisioning_verifier",
    "secret_values_exposed": False,
    "all_required_values_present": len(all_missing) == 0,
    "missing_count": len(all_missing),
    "sections": sections,
    "owner_approval_required_before_live_execution": True,
    "live_external_actions_enabled": False,
    "generated_at": datetime.utcnow().isoformat()
}

out = ROOT / "telemetry" / "activation" / "live-production-provisioning-verifier.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("LIVE_PRODUCTION_PROVISIONING_VERIFIER_COMPLETED")
print("SECRET_VALUES_EXPOSED:false")
print("ALL_REQUIRED_VALUES_PRESENT:", report["all_required_values_present"])
print("MISSING_COUNT:", report["missing_count"])
