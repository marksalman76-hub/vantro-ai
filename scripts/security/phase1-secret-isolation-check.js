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
