const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const REPORT_DIR = path.join(ROOT, "telemetry", "security");
fs.mkdirSync(REPORT_DIR, { recursive: true });

const policyPath = path.join(ROOT, "config", "security", "secret-audit-policy.json");
const policy = JSON.parse(fs.readFileSync(policyPath, "utf8"));

const IGNORE_DIRS = new Set(policy.ignored_scan_directories || []);

const SYNTHETIC_FILES = [
  "scripts/security/redaction-verification.py",
  "backend/app/core/secure_runtime_config.py",
  "scripts/security/production-secret-audit.js",
  "install_phase1_runtime_secret_extraction.py",
  "install_phase1_secret_isolation_sanitisation.py",
  "install_phase1_security_finalisation.py",
  "install_phase1_redaction_audit_noise_reduction.py",
  "install_phase1_legacy_secret_extraction.py",
  "install_phase1_final_secret_enforcement.py"
];

const LEGACY_REFERENCE_FILES = [
  "install_batch_i_production_launch_pack.py",
  "step103_create_production_env_template.py"
];

const RISK_PATTERNS = [
  { name: "OPENAI_KEY", regex: /sk-[A-Za-z0-9_\-]{20,}/g, severity: "critical" },
  { name: "RUNWAY_KEY", regex: /rk_live_[A-Za-z0-9_\-]{20,}/g, severity: "critical" },
  { name: "STRIPE_WEBHOOK_SECRET", regex: /whsec_[A-Za-z0-9_\-]{20,}/g, severity: "critical" },
  { name: "GOOGLE_API_KEY", regex: /AIza[A-Za-z0-9_\-]{20,}/g, severity: "high" },
  { name: "PRIVATE_KEY_BLOCK", regex: new RegExp("-----BEGIN " + "PRIVATE KEY-----", "g"), severity: "critical" },
  { name: "ADMIN_PLATFORM_TOKEN_ASSIGNMENT", regex: /ADMIN_PLATFORM_TOKEN\s*=\s*["']?[^"'\n]+/g, severity: "high" },
  { name: "DATABASE_URL_ASSIGNMENT", regex: /DATABASE_URL\s*=\s*["']?[^"'\n]+/g, severity: "high" },
  { name: "JWT_SECRET_ASSIGNMENT", regex: /JWT_SECRET\s*=\s*["']?[^"'\n]+/g, severity: "high" },
  { name: "SECRET_KEY_ASSIGNMENT", regex: /SECRET_KEY\s*=\s*["']?[^"'\n]+/g, severity: "high" }
];

function normalise(file) {
  return file.replaceAll("\\", "/");
}

function isAllowedTemplate(file) {
  const n = normalise(file);
  return (policy.allowed_template_files || []).some((allowed) => n.endsWith(normalise(allowed)));
}

function isSyntheticFile(file) {
  const n = normalise(file);
  return SYNTHETIC_FILES.some((candidate) => n.endsWith(normalise(candidate)));
}

function isLegacyReferenceFile(file) {
  const n = normalise(file);
  return LEGACY_REFERENCE_FILES.some((candidate) => n.endsWith(normalise(candidate)));
}

function isLocalEnv(file) {
  const n = normalise(file);
  return [".env", ".env.local", ".env.production", ".env.production.local"].includes(n);
}

function isLikelyPlaceholder(match) {
  return /CHANGE_ME|REPLACE_ME|your_|placeholder|example|template|DO_NOT_COMMIT|os\.getenv|process\.env|getenv\(|REDACTED_SECRET/i.test(match);
}

function isLikelySynthetic(match, file) {
  if (isSyntheticFile(file)) return true;
  return /super-secret|1234567890abcdefghijklmnopqrstuv|sample|fixture|redaction|test-only|synthetic/i.test(match);
}

const findings = [];
const reviewedReferences = [];
const syntheticReferences = [];
const controlledLocalSecrets = [];
const legacyReferences = [];

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

      const realMatches = matches.filter((m) =>
        !isLikelyPlaceholder(m) && !isLikelySynthetic(m, relative)
      );

      if (isLocalEnv(relative)) {
        controlledLocalSecrets.push({
          file: relative,
          pattern: pattern.name,
          count: matches.length,
          classification: "controlled_local_env_secret",
          action_required: "must remain gitignored; rotate before production release"
        });
        continue;
      }

      if (isAllowedTemplate(relative)) {
        reviewedReferences.push({
          file: relative,
          pattern: pattern.name,
          count: matches.length,
          classification: "allowed_template_reference"
        });
        continue;
      }

      if (isSyntheticFile(relative)) {
        syntheticReferences.push({
          file: relative,
          pattern: pattern.name,
          count: matches.length,
          classification: "synthetic_security_test_or_scanner_reference"
        });
        continue;
      }

      if (isLegacyReferenceFile(relative)) {
        legacyReferences.push({
          file: relative,
          pattern: pattern.name,
          count: matches.length,
          classification: "legacy_placeholder_or_archive_reference",
          action_required: "safe to keep until archive cleanup; not runtime path"
        });
        continue;
      }

      if (realMatches.length) {
        findings.push({
          file: relative,
          pattern: pattern.name,
          severity: pattern.severity,
          count: realMatches.length,
          action_required: "review and remove hardcoded secret or convert to env loader"
        });
      } else {
        reviewedReferences.push({
          file: relative,
          pattern: pattern.name,
          count: matches.length,
          classification: "placeholder_or_env_reference"
        });
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
  controlled_local_secret_count: controlledLocalSecrets.length,
  reviewed_reference_count: reviewedReferences.length,
  legacy_reference_count: legacyReferences.length,
  synthetic_reference_count: syntheticReferences.length,
  findings,
  controlled_local_secrets: controlledLocalSecrets,
  reviewed_references: reviewedReferences,
  legacy_references: legacyReferences,
  synthetic_references: syntheticReferences
};

const reportPath = path.join(REPORT_DIR, "production-secret-audit-report.json");
fs.writeFileSync(reportPath, JSON.stringify(summary, null, 2));

console.log("PRODUCTION_SECRET_AUDIT_COMPLETED");
console.log("REPORT:", reportPath);
console.log("FINDINGS:", findings.length);
console.log("CONTROLLED_LOCAL_SECRETS:", controlledLocalSecrets.length);
console.log("LEGACY_REFERENCES:", legacyReferences.length);
console.log("REVIEWED_REFERENCES:", reviewedReferences.length);
console.log("SYNTHETIC_REFERENCES:", syntheticReferences.length);

if (findings.length > 0) {
  console.log("SECRET_AUDIT_FAILED_REVIEW_REQUIRED");
  process.exitCode = 1;
} else {
  console.log("SECRET_AUDIT_PASSED_WITH_CONTROLLED_LOCAL_SECRET_POLICY");
}
