const { spawnSync } = require("child_process");

const commands = [
  ["python", ["scripts/monitoring/operational-monitoring-runtime.py"]],
  ["python", ["scripts/recovery/incident-response-runtime.py"]],
  ["python", ["scripts/providers/provider-failover-runtime.py"]],
  ["python", ["scripts/database/postgres-backup-restore-runtime.py"]],
  ["python", ["scripts/monitoring/live-operational-telemetry.py"]],
  ["python", ["scripts/providers/provider-health-scoring.py"]],
  ["python", ["scripts/monitoring/queue-degradation-detection.py"]],
  ["python", ["scripts/recovery/incident-packet-runtime.py"]],
  ["python", ["scripts/monitoring/alert-escalation-pipeline.py"]],
  ["python", ["scripts/providers/circuit-breaker-runtime.py"]],
  ["python", ["scripts/database/restore-simulation-runtime.py"]]
];

let failed = false;

for (const [cmd, args] of commands) {
  console.log("\nRUNNING:", cmd, args.join(" "));
  const result = spawnSync(cmd, args, { stdio: "inherit", shell: false });
  if (result.status !== 0) failed = true;
}

if (failed) {
  console.log("\nPHASE2_LIVE_OPS_CHECK_FAILED");
  process.exit(1);
}

console.log("\nPHASE2_LIVE_OPS_CHECK_PASSED");
