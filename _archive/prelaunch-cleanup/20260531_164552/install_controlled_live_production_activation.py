from pathlib import Path
from datetime import datetime
import json
import shutil

ROOT = Path.cwd()
STAMP = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / "production" / f"controlled_live_activation_before_{STAMP}"
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

write("config/controlled-live-activation-policy.json", json.dumps({
    "phase": "Controlled Live Production Activation",
    "mode": "pre_activation_gate",
    "live_external_actions_enabled": False,
    "production_secret_rotation_executed": False,
    "production_high_volume_load_executed": False,
    "owner_approval_required": True,
    "required_before_activation": [
        "production secrets provisioned",
        "rollback values stored securely",
        "monitoring reviewed",
        "provider readiness verified",
        "database backup readiness verified",
        "owner approval recorded"
    ],
    "blocked_actions_until_approval": [
        "live provider execution",
        "live payment execution",
        "live email sending",
        "live database restore",
        "high-volume production load testing",
        "provider saturation testing"
    ]
}, indent=2))

write("scripts/activation/live-activation-readiness.py", r"""
from pathlib import Path
from datetime import datetime
import json

ROOT = Path.cwd()

security_dir = ROOT / "telemetry" / "security"
ops_dir = ROOT / "telemetry" / "operations"
load_dir = ROOT / "telemetry" / "load-testing"

def read(path):
    if not path.exists():
        return {"success": False, "missing": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))

phase1 = read(security_dir / "phase1-final-completion-verifier.json")
phase2 = read(ops_dir / "phase2-completion-verifier.json")
phase3 = read(load_dir / "phase3-readiness-verifier.json")
env = read(security_dir / "production-env-validator.json")
provider = read(security_dir / "provider-secret-enforcement.json")

report = {
    "success": (
        phase1.get("success") is True
        and phase2.get("success") is True
        and phase3.get("success") is True
    ),
    "mode": "pre_activation_readiness",
    "live_external_actions_enabled": False,
    "owner_approval_required": True,
    "phase_foundations": {
        "phase1_security": phase1.get("success") is True,
        "phase2_operations": phase2.get("success") is True,
        "phase3_scaling_governance": phase3.get("success") is True
    },
    "production_env_ready": env.get("success") is True,
    "provider_secret_enforcement_ready": provider.get("success") is True,
    "activation_state": "foundations_ready_live_secrets_pending",
    "next_owner_actions": [
        "rotate and provision production secrets",
        "verify Render/Vercel/Supabase env values",
        "run live provider readiness validation",
        "approve controlled live load window",
        "run final production activation verifier"
    ],
    "generated_at": datetime.utcnow().isoformat()
}

out = ROOT / "telemetry" / "activation" / "live-activation-readiness.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("LIVE_ACTIVATION_READINESS_READY")
print("ACTIVATION_STATE:", report["activation_state"])
print("LIVE_EXTERNAL_ACTIONS_ENABLED:false")
""")

write("scripts/activation/owner-approval-gate.py", r"""
from pathlib import Path
from datetime import datetime
import json
import os

ROOT = Path.cwd()

approval = os.getenv("OWNER_APPROVED_LIVE_ACTIVATION", "").lower() == "true"

report = {
    "success": True,
    "owner_approval_gate_ready": True,
    "owner_approved_live_activation": approval,
    "live_external_actions_allowed": approval,
    "blocked_if_false": [
        "provider execution",
        "payment execution",
        "email sending",
        "database restore",
        "high-volume load test",
        "provider saturation test"
    ],
    "generated_at": datetime.utcnow().isoformat()
}

out = ROOT / "telemetry" / "activation" / "owner-approval-gate.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("OWNER_APPROVAL_GATE_READY")
print("OWNER_APPROVED_LIVE_ACTIVATION:", approval)
print("LIVE_EXTERNAL_ACTIONS_ALLOWED:", approval)
""")

write("scripts/activation/live-provider-activation-gate.py", r"""
from pathlib import Path
from datetime import datetime
import json
import os

ROOT = Path.cwd()

required = {
    "openai": ["OPENAI_API_KEY"],
    "stripe": ["STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"],
    "email": ["SMTP_PASSWORD", "BREVO_API_KEY"],
    "database": ["DATABASE_URL"],
    "supabase": ["SUPABASE_SERVICE_ROLE_KEY"],
}

providers = {}
for provider, secrets in required.items():
    missing = [name for name in secrets if not os.getenv(name)]
    providers[provider] = {
        "ready": len(missing) == 0,
        "missing": missing,
        "live_execution_allowed": False
    }

report = {
    "success": True,
    "live_provider_activation_gate_ready": True,
    "live_provider_execution_enabled": False,
    "providers": providers,
    "generated_at": datetime.utcnow().isoformat()
}

out = ROOT / "telemetry" / "activation" / "live-provider-activation-gate.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("LIVE_PROVIDER_ACTIVATION_GATE_READY")
print("LIVE_PROVIDER_EXECUTION_ENABLED:false")
""")

write("scripts/activation/live-load-activation-gate.py", r"""
from pathlib import Path
from datetime import datetime
import json
import os

ROOT = Path.cwd()

approved = os.getenv("OWNER_APPROVED_LIVE_LOAD_TEST", "").lower() == "true"

report = {
    "success": True,
    "live_load_activation_gate_ready": True,
    "owner_approved_live_load_test": approved,
    "high_volume_load_allowed": approved,
    "default_allowed_without_owner_approval": "dry_run_or_safe_low_volume_only",
    "generated_at": datetime.utcnow().isoformat()
}

out = ROOT / "telemetry" / "activation" / "live-load-activation-gate.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("LIVE_LOAD_ACTIVATION_GATE_READY")
print("HIGH_VOLUME_LOAD_ALLOWED:", approved)
""")

write("scripts/activation/controlled-live-activation-check.js", r"""
const { spawnSync } = require("child_process");

const commands = [
  ["python", ["scripts/activation/live-activation-readiness.py"]],
  ["python", ["scripts/activation/owner-approval-gate.py"]],
  ["python", ["scripts/activation/live-provider-activation-gate.py"]],
  ["python", ["scripts/activation/live-load-activation-gate.py"]]
];

let failed = false;

for (const [cmd, args] of commands) {
  console.log("\nRUNNING:", cmd, args.join(" "));
  const result = spawnSync(cmd, args, { stdio: "inherit", shell: false });
  if (result.status !== 0) failed = true;
}

if (failed) {
  console.log("\nCONTROLLED_LIVE_ACTIVATION_CHECK_FAILED");
  process.exit(1);
}

console.log("\nCONTROLLED_LIVE_ACTIVATION_CHECK_PASSED");
""")

print("CONTROLLED_LIVE_PRODUCTION_ACTIVATION_INSTALLED")
print("Backup:", BACKUP)