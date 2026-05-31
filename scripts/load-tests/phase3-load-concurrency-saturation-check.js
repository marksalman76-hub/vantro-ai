const { spawnSync } = require("child_process");

const commands = [
  ["python", ["scripts/load-tests/load-test-dryrun-runtime.py"]],
  ["python", ["scripts/load-tests/concurrency-simulation-runtime.py"]],
  ["python", ["scripts/providers/provider-saturation-governance.py"]],
  ["python", ["scripts/load-tests/worker-pressure-telemetry.py"]],
  ["python", ["scripts/load-tests/retry-storm-prevention.py"]],
  ["python", ["scripts/load-tests/concurrency-sla-scoring.py"]],
  ["python", ["scripts/load-tests/phase3-readiness-verifier.py"]]
];

let failed = false;

for (const [cmd, args] of commands) {
  console.log("\nRUNNING:", cmd, args.join(" "));
  const result = spawnSync(cmd, args, { stdio: "inherit", shell: false });
  if (result.status !== 0) failed = true;
}

if (failed) {
  console.log("\nPHASE3_LOAD_CONCURRENCY_SATURATION_CHECK_FAILED");
  process.exit(1);
}

console.log("\nPHASE3_LOAD_CONCURRENCY_SATURATION_CHECK_PASSED");
