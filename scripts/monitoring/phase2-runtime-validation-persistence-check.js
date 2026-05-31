const { spawnSync } = require("child_process");

const commands = [
  ["node", ["scripts/monitoring/phase2-live-ops-check.js"]],
  ["python", ["scripts/monitoring/operational-persistence-runtime.py"]],
  ["python", ["scripts/providers/provider-recovery-scoring.py"]],
  ["python", ["scripts/recovery/incident-history-registry.py"]],
  ["python", ["scripts/database/backup-manifest-runtime.py"]],
  ["python", ["scripts/monitoring/operational-dashboard-feed.py"]],
  ["python", ["scripts/monitoring/runtime-sla-scoring.py"]],
  ["python", ["scripts/monitoring/phase2-completion-verifier.py"]]
];

let failed = false;

for (const [cmd, args] of commands) {
  console.log("\nRUNNING:", cmd, args.join(" "));
  const result = spawnSync(cmd, args, { stdio: "inherit", shell: false });
  if (result.status !== 0) failed = true;
}

if (failed) {
  console.log("\nPHASE2_RUNTIME_VALIDATION_PERSISTENCE_CHECK_FAILED");
  process.exit(1);
}

console.log("\nPHASE2_RUNTIME_VALIDATION_PERSISTENCE_CHECK_PASSED");
