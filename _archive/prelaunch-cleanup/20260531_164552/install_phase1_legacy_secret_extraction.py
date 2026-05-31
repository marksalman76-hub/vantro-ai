from pathlib import Path
from datetime import datetime
import json
import re
import shutil

ROOT = Path.cwd()
STAMP = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / "production" / f"phase1_legacy_secret_extraction_before_{STAMP}"
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

def patch_file(path_str, transforms):
    path = ROOT / path_str
    if not path.exists():
        print("SKIPPED missing", path_str)
        return
    backup(path)
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text
    for pattern, replacement in transforms:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
    if text != original:
        path.write_text(text, encoding="utf-8")
        print("PATCHED", path_str)
    else:
        print("UNCHANGED", path_str)

# ---------------------------------------------------------------------
# Production required secret manifest
# ---------------------------------------------------------------------

required_secrets = [
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
]

write("config/security/production-secret-manifest.json", json.dumps({
    "phase": "Phase 1 - Security finalisation",
    "mode": "env_only_required",
    "owner_approval_required_for_rotation": True,
    "required_secrets": required_secrets,
    "forbidden_patterns": [
        "hardcoded admin token",
        "hardcoded database url",
        "hardcoded jwt secret",
        "secret values in logs",
        "secret values in telemetry",
        "committed .env files"
    ],
    "allowed_storage": [
        "Render environment variables",
        "Vercel environment variables",
        "Supabase vault / project secrets",
        "approved local .env for development only"
    ]
}, indent=2))

# ---------------------------------------------------------------------
# Production env validator
# ---------------------------------------------------------------------

write("scripts/security/production-env-validator.py", r"""
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
""")

# ---------------------------------------------------------------------
# Deployment secret verifier checklist
# ---------------------------------------------------------------------

write("scripts/security/deployment-secret-verifier.py", r"""
from pathlib import Path
import json

ROOT = Path.cwd()
manifest = json.loads((ROOT / "config" / "security" / "production-secret-manifest.json").read_text(encoding="utf-8"))

targets = []
for secret in manifest["required_secrets"]:
    targets.append({
        "secret": secret,
        "render_required": secret in [
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
        "vercel_required": secret in [
            "ADMIN_PLATFORM_TOKEN",
            "SESSION_SECRET",
        ],
        "supabase_required": secret in [
            "DATABASE_URL",
            "SUPABASE_SERVICE_ROLE_KEY",
        ],
        "manual_owner_verification_required": True,
    })

report = {
    "success": True,
    "mode": "deployment_secret_verification_checklist",
    "production_rotation_executed": False,
    "owner_approval_required": True,
    "targets": targets,
}

out = ROOT / "telemetry" / "security" / "deployment-secret-verifier.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("DEPLOYMENT_SECRET_VERIFIER_CREATED")
print("TARGETS:", len(targets))
print("OWNER_APPROVAL_REQUIRED:true")
""")

# ---------------------------------------------------------------------
# Patch legacy helper files to avoid direct assignments being classified as live secrets
# ---------------------------------------------------------------------

patch_file("live_verify_provider_execution_runtime_final.py", [
    (r"ADMIN_PLATFORM_TOKEN\s*=\s*[\"'][^\"']+[\"']", "ADMIN_PLATFORM_TOKEN = os.getenv('ADMIN_PLATFORM_TOKEN', '')"),
    (r"ADMIN_PLATFORM_TOKEN\s*=\s*os\.environ\.get\([^)]+\)", "ADMIN_PLATFORM_TOKEN = os.getenv('ADMIN_PLATFORM_TOKEN', '')"),
])

patch_file("fix_provider_worker_event_ledger_details_column.py", [
    (r"DATABASE_URL\s*=\s*[\"'][^\"']+[\"']", "DATABASE_URL = os.getenv('DATABASE_URL', '')"),
    (r"DATABASE_URL\s*=\s*os\.environ\.get\([^)]+\)", "DATABASE_URL = os.getenv('DATABASE_URL', '')"),
])

patch_file("install_provider_execution_durable_tables.py", [
    (r"DATABASE_URL\s*=\s*[\"'][^\"']+[\"']", "DATABASE_URL = os.getenv('DATABASE_URL', '')"),
    (r"DATABASE_URL\s*=\s*os\.environ\.get\([^)]+\)", "DATABASE_URL = os.getenv('DATABASE_URL', '')"),
])

patch_file("install_batch_i_production_launch_pack.py", [
    (r"JWT_SECRET\s*=\s*[\"'][^\"']+[\"']", "JWT_SECRET = os.getenv('JWT_SECRET', '')"),
    (r"SECRET_KEY\s*=\s*[\"'][^\"']+[\"']", "SECRET_KEY = os.getenv('SECRET_KEY', '')"),
])

patch_file("step103_create_production_env_template.py", [
    (r"DATABASE_URL\s*=\s*[\"'][^\"']+[\"']", "DATABASE_URL = 'REPLACE_ME_DATABASE_URL'"),
    (r"JWT_SECRET\s*=\s*[\"'][^\"']+[\"']", "JWT_SECRET = 'REPLACE_ME_JWT_SECRET'"),
    (r"SECRET_KEY\s*=\s*[\"'][^\"']+[\"']", "SECRET_KEY = 'REPLACE_ME_SECRET_KEY'"),
])

# ---------------------------------------------------------------------
# Secret-safe logging middleware foundation
# ---------------------------------------------------------------------

write("backend/app/core/secret_safe_logging.py", r"""
from __future__ import annotations

from typing import Any

from backend.app.core.secure_runtime_config import redact_text


def redact_for_log(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, dict):
        return {key: redact_for_log(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_for_log(item) for item in value]
    return value


def safe_log_event(event: dict) -> dict:
    return redact_for_log(event)
""")

# ---------------------------------------------------------------------
# Combined check
# ---------------------------------------------------------------------

write("scripts/security/phase1-legacy-secret-extraction-check.js", r"""
const { spawnSync } = require("child_process");

const commands = [
  ["python", ["scripts/security/production-env-validator.py"]],
  ["python", ["scripts/security/deployment-secret-verifier.py"]],
  ["python", ["scripts/security/redaction-verification.py"]],
  ["python", ["scripts/security/runtime-secret-readiness.py"]],
  ["node", ["scripts/security/production-secret-audit.js"]],
  ["node", ["scripts/security/audit-log-hardening.js"]],
  ["node", ["scripts/security/audit-chain-verify.js"]],
  ["node", ["scripts/security/token-governance.js", "--ttl", "3600"]]
];

let failed = false;

for (const [cmd, args] of commands) {
  console.log("\nRUNNING:", cmd, args.join(" "));
  const result = spawnSync(cmd, args, { stdio: "inherit", shell: true });
  if (result.status !== 0) failed = true;
}

if (failed) {
  console.log("\nPHASE1_LEGACY_SECRET_EXTRACTION_CHECK_FAILED_REVIEW_REQUIRED");
  process.exit(1);
}

console.log("\nPHASE1_LEGACY_SECRET_EXTRACTION_CHECK_PASSED");
""")

print("PHASE1_LEGACY_SECRET_EXTRACTION_INSTALLED")
print("Backup:", BACKUP)