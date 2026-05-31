from pathlib import Path
from datetime import datetime
import json
import shutil

ROOT = Path.cwd()
STAMP = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / "production" / f"live_production_provisioning_before_{STAMP}"
BACKUP.mkdir(parents=True, exist_ok=True)

def backup(path: Path):
    if path.exists() and path.is_file():
        target = BACKUP / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)

def write(path_str, content):
    path = ROOT / path_str
    backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print("UPDATED", path_str)

write("docs/runbooks/live-production-provisioning-checklist.md", """
# Live Production Provisioning Checklist

## Owner-controlled actions

Do not paste secrets into chat or commit them to Git.

### Render backend required secrets
- ADMIN_PLATFORM_TOKEN
- JWT_SECRET
- SESSION_SECRET
- DATABASE_URL
- OPENAI_API_KEY
- STRIPE_SECRET_KEY
- STRIPE_WEBHOOK_SECRET
- SMTP_PASSWORD
- BREVO_API_KEY
- SUPABASE_SERVICE_ROLE_KEY

### Vercel frontend required secrets
- ADMIN_PLATFORM_TOKEN
- SESSION_SECRET

### Supabase required secrets
- DATABASE_URL
- SUPABASE_SERVICE_ROLE_KEY

## Required before enabling live execution
1. Rotate production secrets directly inside provider dashboards.
2. Store rollback values securely outside the repository.
3. Add new values to Render/Vercel/Supabase environment settings.
4. Redeploy backend and frontend after environment updates.
5. Run the controlled activation verifier.
6. Only then approve low-volume live execution.
""")

write("scripts/activation/live-production-provisioning-verifier.py", r"""
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
""")

write("scripts/activation/final-live-activation-verifier.py", r"""
from pathlib import Path
from datetime import datetime
import json
import os

ROOT = Path.cwd()
activation = ROOT / "telemetry" / "activation"

def read(name):
    path = activation / name
    if not path.exists():
        return {"success": False, "missing": name}
    return json.loads(path.read_text(encoding="utf-8"))

provisioning = read("live-production-provisioning-verifier.json")

owner_approved = os.getenv("OWNER_APPROVED_LIVE_ACTIVATION", "").lower() == "true"
load_approved = os.getenv("OWNER_APPROVED_LIVE_LOAD_TEST", "").lower() == "true"

report = {
    "success": provisioning.get("success") is True and owner_approved,
    "mode": "final_live_activation_verifier",
    "provisioning_ready": provisioning.get("success") is True,
    "owner_approved_live_activation": owner_approved,
    "owner_approved_live_load_test": load_approved,
    "live_provider_execution_allowed": provisioning.get("success") is True and owner_approved,
    "high_volume_load_allowed": provisioning.get("success") is True and owner_approved and load_approved,
    "secret_values_exposed": False,
    "activation_state": (
        "live_activation_allowed"
        if provisioning.get("success") is True and owner_approved
        else "blocked_pending_provisioning_or_owner_approval"
    ),
    "generated_at": datetime.utcnow().isoformat()
}

out = activation / "final-live-activation-verifier.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("FINAL_LIVE_ACTIVATION_VERIFIER_COMPLETED")
print("ACTIVATION_STATE:", report["activation_state"])
print("LIVE_PROVIDER_EXECUTION_ALLOWED:", report["live_provider_execution_allowed"])
print("HIGH_VOLUME_LOAD_ALLOWED:", report["high_volume_load_allowed"])
""")

write("scripts/activation/live-production-provisioning-check.js", r"""
const { spawnSync } = require("child_process");

const commands = [
  ["python", ["scripts/activation/live-production-provisioning-verifier.py"]],
  ["python", ["scripts/activation/final-live-activation-verifier.py"]]
];

let failed = false;

for (const [cmd, args] of commands) {
  console.log("\nRUNNING:", cmd, args.join(" "));
  const result = spawnSync(cmd, args, { stdio: "inherit", shell: false });
  if (result.status !== 0) failed = true;
}

if (failed) {
  console.log("\nLIVE_PRODUCTION_PROVISIONING_CHECK_FAILED");
  process.exit(1);
}

console.log("\nLIVE_PRODUCTION_PROVISIONING_CHECK_PASSED");
""")

print("LIVE_PRODUCTION_PROVISIONING_VERIFIER_INSTALLED")
print("Backup:", BACKUP)