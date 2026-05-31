const { spawnSync } = require("child_process");

const commands = [
  ["python", ["scripts/security/production-env-validator.py"]],
  ["python", ["scripts/security/deployment-secret-verifier.py"]],
  ["python", ["scripts/security/provider-secret-enforcement.py"]],
  ["python", ["scripts/security/redaction-verification.py"]],
  ["python", ["scripts/security/runtime-secret-readiness.py"]],
  ["node", ["scripts/security/production-secret-audit.js"]],
  ["node", ["scripts/security/audit-log-hardening.js"]],
  ["node", ["scripts/security/audit-chain-verify.js"]],
  ["node", ["scripts/security/token-governance.js", "--ttl", "3600"]],
  ["python", ["scripts/security/phase1-final-completion-verifier.py"]]
];

let failed = false;

for (const [cmd, args] of commands) {
  console.log("\nRUNNING:", cmd, args.join(" "));
  const result = spawnSync(cmd, args, { stdio: "inherit", shell: true });
  if (result.status !== 0) failed = true;
}

if (failed) {
  console.log("\nPHASE1_FINAL_SECRET_ENFORCEMENT_CHECK_FAILED_REVIEW_REQUIRED");
  process.exit(1);
}

console.log("\nPHASE1_FINAL_SECRET_ENFORCEMENT_CHECK_PASSED");
