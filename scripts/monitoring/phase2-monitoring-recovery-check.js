const { spawnSync } = require("child_process");

const commands = [
  ["python", ["scripts/monitoring/operational-monitoring-runtime.py"]],
  ["python", ["scripts/recovery/incident-response-runtime.py"]],
  ["python", ["scripts/providers/provider-failover-runtime.py"]],
  ["python", ["scripts/database/postgres-backup-restore-runtime.py"]]
];

let failed = false;

for (const [cmd, args] of commands) {
  console.log("\nRUNNING:", cmd, args.join(" "));
  const result = spawnSync(cmd, args, { stdio: "inherit", shell: true });
  if (result.status !== 0) failed = true;
}

if (failed) {
  console.log("\nPHASE2_MONITORING_RECOVERY_CHECK_FAILED");
  process.exit(1);
}

console.log("\nPHASE2_MONITORING_RECOVERY_CHECK_PASSED");
