from pathlib import Path
from datetime import datetime
import json
import re
import shutil

ROOT = Path.cwd()
STAMP = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / "production" / f"phase1_secret_isolation_before_{STAMP}"
BACKUP.mkdir(parents=True, exist_ok=True)

def backup(path: Path):
    if path.exists():
        target = BACKUP / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.is_file():
            shutil.copy2(path, target)

def write(path_str, content):
    path = ROOT / path_str
    backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print("UPDATED", path_str)

def append_gitignore():
    gi = ROOT / ".gitignore"
    backup(gi)
    existing = gi.read_text(encoding="utf-8", errors="ignore") if gi.exists() else ""
    block = """

# Production secret protection
.env
.env.*
!.env.example
!.env.template
telemetry/security/*secret*
telemetry/security/*audit-report*
logs/*.log
"""
    if "Production secret protection" not in existing:
        gi.write_text(existing.rstrip() + block + "\n", encoding="utf-8")
        print("UPDATED .gitignore")
    else:
        print("UNCHANGED .gitignore")

append_gitignore()

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
        "archive"
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

write("scripts/security/production-secret-audit.js", r"""
const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const REPORT_DIR = path.join(ROOT, "telemetry", "security");
fs.mkdirSync(REPORT_DIR, { recursive: true });

const policyPath = path.join(ROOT, "config", "security", "secret-audit-policy.json");
const policy = JSON.parse(fs.readFileSync(policyPath, "utf8"));

const IGNORE_DIRS = new Set(policy.ignored_scan_directories || []);

const RISK_PATTERNS = [
  { name: "OPENAI_KEY", regex: /sk-[A-Za-z0-9_\-]{20,}/g, severity: "critical" },
  { name: "RUNWAY_KEY", regex: /rk_live_[A-Za-z0-9_\-]{20,}/g, severity: "critical" },
  { name: "STRIPE_WEBHOOK_SECRET", regex: /whsec_[A-Za-z0-9_\-]{20,}/g, severity: "critical" },
  { name: "GOOGLE_API_KEY", regex: /AIza[A-Za-z0-9_\-]{20,}/g, severity: "high" },
  { name: "PRIVATE_KEY_BLOCK", regex: /-----BEGIN PRIVATE KEY-----/g, severity: "critical" },
  { name: "ADMIN_PLATFORM_TOKEN_ASSIGNMENT", regex: /ADMIN_PLATFORM_TOKEN\s*=\s*["']?[^"'\n]+/g, severity: "high" },
  { name: "DATABASE_URL_ASSIGNMENT", regex: /DATABASE_URL\s*=\s*["']?[^"'\n]+/g, severity: "high" },
  { name: "JWT_SECRET_ASSIGNMENT", regex: /JWT_SECRET\s*=\s*["']?[^"'\n]+/g, severity: "high" },
  { name: "SECRET_KEY_ASSIGNMENT", regex: /SECRET_KEY\s*=\s*["']?[^"'\n]+/g, severity: "high" }
];

function isAllowedTemplate(file) {
  return (policy.allowed_template_files || []).some((allowed) =>
    file.replaceAll("\\", "/").endsWith(allowed.replaceAll("\\", "/"))
  );
}

function isLocalEnv(file) {
  const normalized = file.replaceAll("\\", "/");
  return [".env", ".env.local", ".env.production", ".env.production.local"].includes(normalized);
}

function isLikelyPlaceholder(match) {
  return /CHANGE_ME|REPLACE_ME|your_|placeholder|example|template|DO_NOT_COMMIT|os\.getenv|process\.env|getenv\(/i.test(match);
}

const findings = [];
const reviewedReferences = [];

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (IGNORE_DIRS.has(entry.name)) continue;
    const full = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      walk(full);
      continue;
    }

    if (!/\.(js|ts|tsx|py|json|env|md|cmd|txt|yml|yaml)$/i.test(entry.name)) continue;

    const relative = path.relative(ROOT, full);
    const text = fs.readFileSync(full, "utf8");

    for (const pattern of RISK_PATTERNS) {
      const matches = [...text.matchAll(pattern.regex)].map((m) => m[0]);
      if (!matches.length) continue;

      const realMatches = matches.filter((m) => !isLikelyPlaceholder(m));

      if (isAllowedTemplate(relative)) {
        reviewedReferences.push({ file: relative, pattern: pattern.name, count: matches.length, classification: "allowed_template_reference" });
        continue;
      }

      if (realMatches.length) {
        findings.push({
          file: relative,
          pattern: pattern.name,
          severity: pattern.severity,
          count: realMatches.length,
          local_env_file: isLocalEnv(relative),
          action_required: isLocalEnv(relative)
            ? "confirm file is gitignored and rotate before production release"
            : "review and remove hardcoded secret or convert to env loader"
        });
      } else {
        reviewedReferences.push({ file: relative, pattern: pattern.name, count: matches.length, classification: "placeholder_or_env_reference" });
      }
    }
  }
}

walk(ROOT);

const summary = {
  success: findings.length === 0,
  generated_at: new Date().toISOString(),
  scanned_root: ROOT,
  ignored_directories: [...IGNORE_DIRS],
  finding_count: findings.length,
  reviewed_reference_count: reviewedReferences.length,
  findings,
  reviewed_references: reviewedReferences
};

const reportPath = path.join(REPORT_DIR, "production-secret-audit-report.json");
fs.writeFileSync(reportPath, JSON.stringify(summary, null, 2));

console.log("PRODUCTION_SECRET_AUDIT_COMPLETED");
console.log("REPORT:", reportPath);
console.log("FINDINGS:", findings.length);
console.log("REVIEWED_REFERENCES:", reviewedReferences.length);

if (findings.length > 0) {
  console.log("SECRET_AUDIT_FAILED_REVIEW_REQUIRED");
  process.exitCode = 1;
} else {
  console.log("SECRET_AUDIT_PASSED");
}
""")

write("scripts/security/secret-inventory-ledger.js", r"""
const fs = require("fs");
const path = require("path");

const policyPath = path.join(process.cwd(), "config", "security", "secret-rotation-policy.json");
const policy = JSON.parse(fs.readFileSync(policyPath, "utf8"));

const ledger = {
  generated_at: new Date().toISOString(),
  production_rotation_executed: false,
  owner_approval_required: true,
  rotation_targets: policy.rotate_targets.map((name) => ({
    name,
    owner_review_required: true,
    rotated: false,
    rollback_ready: false,
    storage_expected: "production host secret manager"
  }))
};

fs.mkdirSync(path.join(process.cwd(), "telemetry", "security"), { recursive: true });
fs.writeFileSync(
  path.join(process.cwd(), "telemetry", "security", "secret-inventory-ledger.json"),
  JSON.stringify(ledger, null, 2)
);

console.log("SECRET_INVENTORY_LEDGER_CREATED");
console.log("TARGETS:", ledger.rotation_targets.length);
""")

write("scripts/security/audit-chain-verify.js", r"""
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const chainPath = path.join(process.cwd(), "telemetry", "security", "audit-hash-chain.json");

if (!fs.existsSync(chainPath)) {
  console.log("AUDIT_CHAIN_VERIFY_FAILED_MISSING_CHAIN");
  process.exit(1);
}

const chain = JSON.parse(fs.readFileSync(chainPath, "utf8"));
let previous = "GENESIS";
let ok = true;

for (const raw of chain) {
  const entry = { ...raw };
  const actualHash = entry.entry_hash;
  delete entry.entry_hash;

  const expectedHash = crypto
    .createHash("sha256")
    .update(JSON.stringify(entry))
    .digest("hex");

  if (entry.previous_hash !== previous || actualHash !== expectedHash) {
    ok = false;
    break;
  }

  previous = actualHash;
}

console.log("AUDIT_CHAIN_ENTRIES:", chain.length);
console.log(ok ? "AUDIT_CHAIN_VERIFY_PASSED" : "AUDIT_CHAIN_VERIFY_FAILED");

if (!ok) process.exit(1);
""")

write("scripts/security/phase1-secret-isolation-check.js", r"""
const { spawnSync } = require("child_process");

const commands = [
  ["node", ["scripts/security/secret-inventory-ledger.js"]],
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
  console.log("\nPHASE1_SECRET_ISOLATION_CHECK_FAILED_REVIEW_REQUIRED");
  process.exit(1);
}

console.log("\nPHASE1_SECRET_ISOLATION_CHECK_PASSED");
""")

print("PHASE1_SECRET_ISOLATION_SANITISATION_INSTALLED")
print("Backup:", BACKUP)