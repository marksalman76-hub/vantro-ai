from pathlib import Path
from datetime import datetime
import json
import shutil

ROOT = Path.cwd()
STAMP = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / "production" / f"phase1_runtime_secret_extraction_before_{STAMP}"
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

def replace_text(path_str, replacements):
    path = ROOT / path_str
    if not path.exists():
        print("SKIPPED missing", path_str)
        return
    backup(path)
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text
    for old, new in replacements:
        text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding="utf-8")
        print("PATCHED", path_str)
    else:
        print("UNCHANGED", path_str)

# ---------------------------------------------------------------------
# Secure runtime config loader
# ---------------------------------------------------------------------

write("backend/app/core/secure_runtime_config.py", r"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Dict, Optional


_SECRET_NAMES = {
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
}


@dataclass(frozen=True)
class SecretCheck:
    name: str
    present: bool
    masked: str
    source: str = "environment"


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(name, default)


def require_secret(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required secret is missing: {name}")
    return value


def mask_secret(value: Optional[str]) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "***"
    return f"{value[:3]}...{value[-3:]}"


def redact_text(value: str) -> str:
    if not value:
        return value

    redacted = value
    patterns = [
        r"sk-[A-Za-z0-9_\-]{20,}",
        r"rk_live_[A-Za-z0-9_\-]{20,}",
        r"whsec_[A-Za-z0-9_\-]{20,}",
        r"AIza[A-Za-z0-9_\-]{20,}",
        r"postgres(?:ql)?://[^\\s\"']+",
        r"ADMIN_PLATFORM_TOKEN\\s*=\\s*[^\\s]+",
        r"JWT_SECRET\\s*=\\s*[^\\s]+",
        r"SESSION_SECRET\\s*=\\s*[^\\s]+",
        r"SECRET_KEY\\s*=\\s*[^\\s]+",
        r"DATABASE_URL\\s*=\\s*[^\\s]+",
    ]

    for pattern in patterns:
        redacted = re.sub(pattern, "[REDACTED_SECRET]", redacted)

    return redacted


def secret_inventory() -> Dict[str, SecretCheck]:
    inventory: Dict[str, SecretCheck] = {}
    for name in sorted(_SECRET_NAMES):
        value = os.getenv(name)
        inventory[name] = SecretCheck(
            name=name,
            present=bool(value),
            masked=mask_secret(value),
        )
    return inventory


def production_secret_readiness() -> Dict[str, object]:
    inventory = secret_inventory()
    missing = [name for name, check in inventory.items() if not check.present]

    return {
        "success": len(missing) == 0,
        "mode": "env_only_secret_access",
        "secret_values_exposed": False,
        "missing": missing,
        "present_count": len(inventory) - len(missing),
        "total_required": len(inventory),
        "inventory": {
            name: {
                "present": check.present,
                "masked": check.masked,
                "source": check.source,
            }
            for name, check in inventory.items()
        },
    }
""")

# ---------------------------------------------------------------------
# Runtime verifier
# ---------------------------------------------------------------------

write("scripts/security/runtime-secret-readiness.py", r"""
from pathlib import Path
import json
import sys

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

from backend.app.core.secure_runtime_config import production_secret_readiness

report = production_secret_readiness()

out_dir = ROOT / "telemetry" / "security"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "runtime-secret-readiness.json").write_text(
    json.dumps(report, indent=2),
    encoding="utf-8",
)

print("RUNTIME_SECRET_READINESS_CHECK_COMPLETED")
print("SECRET_VALUES_EXPOSED:false")
print("PRESENT_COUNT:", report["present_count"])
print("MISSING_COUNT:", len(report["missing"]))

if not report["success"]:
    print("RUNTIME_SECRET_READINESS_NOT_FULLY_CONFIGURED")
""")

# ---------------------------------------------------------------------
# Redaction verifier
# ---------------------------------------------------------------------

write("scripts/security/redaction-verification.py", r"""
from pathlib import Path
import json
import sys

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

from backend.app.core.secure_runtime_config import redact_text

samples = [
    "OPENAI key sk-1234567890abcdefghijklmnopqrstuv",
    "stripe whsec_1234567890abcdefghijklmnopqrstuv",
    "postgresql://user:password@example.com:5432/db",
    "ADMIN_PLATFORM_TOKEN=super-secret-token-value",
    "JWT_SECRET=super-secret-jwt-value",
    "DATABASE_URL=postgresql://user:pass@host:5432/db",
]

results = []
for sample in samples:
    redacted = redact_text(sample)
    results.append({
        "input_contains_secret_shape": True,
        "output": redacted,
        "redacted": "[REDACTED_SECRET]" in redacted,
    })

success = all(item["redacted"] for item in results)

report = {
    "success": success,
    "secret_values_exposed": False,
    "results": results,
}

out_dir = ROOT / "telemetry" / "security"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "redaction-verification.json").write_text(
    json.dumps(report, indent=2),
    encoding="utf-8",
)

print("REDACTION_VERIFICATION_COMPLETED")
print("REDACTION_SUCCESS:", success)

if not success:
    raise SystemExit(1)
""")

# ---------------------------------------------------------------------
# Harden production secret audit against self-report loops
# ---------------------------------------------------------------------

write("config/security/secret-audit-policy.json", json.dumps({
    "phase": "Phase 1 - Security finalisation",
    "mode": "production_sanitisation",
    "real_secret_files_never_commit": [
        ".env",
        ".env.local",
        ".env.production",
        ".env.production.local"
    ],
    "allowed_template_files": [
        ".env.example",
        ".env.template",
        "docs/PRODUCTION_ENVIRONMENT_TEMPLATE_DO_NOT_COMMIT_SECRETS.env"
    ],
    "ignored_scan_directories": [
        ".git",
        "node_modules",
        ".next",
        ".venv",
        "venv",
        "backups",
        "archive",
        "telemetry"
    ],
    "expected_reference_files": [
        "backend/app/core",
        "scripts/security",
        "docs"
    ],
    "requires_manual_review_if": [
        "actual secret-looking values detected",
        "ADMIN_PLATFORM_TOKEN assignment outside local env",
        "DATABASE_URL literal with host/password",
        "private key block outside template"
    ]
}, indent=2))

# Avoid self-triggering on the literal private-key marker inside scanner source
replace_text("scripts/security/production-secret-audit.js", [
    ('{ name: "PRIVATE_KEY_BLOCK", regex: /-----BEGIN PRIVATE KEY-----/g, severity: "critical" },',
     '{ name: "PRIVATE_KEY_BLOCK", regex: new RegExp("-----BEGIN " + "PRIVATE KEY-----", "g"), severity: "critical" },')
])

# ---------------------------------------------------------------------
# Combined check for this block
# ---------------------------------------------------------------------

write("scripts/security/phase1-runtime-secret-extraction-check.js", r"""
const { spawnSync } = require("child_process");

const commands = [
  ["python", ["scripts/security/runtime-secret-readiness.py"]],
  ["python", ["scripts/security/redaction-verification.py"]],
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
  console.log("\nPHASE1_RUNTIME_SECRET_EXTRACTION_CHECK_FAILED_REVIEW_REQUIRED");
  process.exit(1);
}

console.log("\nPHASE1_RUNTIME_SECRET_EXTRACTION_CHECK_PASSED");
""")

print("PHASE1_RUNTIME_SECRET_EXTRACTION_INSTALLED")
print("Backup:", BACKUP)