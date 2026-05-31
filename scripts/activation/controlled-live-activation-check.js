const { spawnSync } = require("child_process");

const commands = [
  ["python", ["scripts/activation/live-activation-readiness.py"]],
  ["python", ["scripts/activation/owner-approval-gate.py"]],
  ["python", ["scripts/activation/live-provider-activation-gate.py"]],
  ["python", ["scripts/activation/live-load-activation-gate.py"]]
];

let failed = false;

for (const [cmd, args] of commands) {
  console.log("\nRUNNING:", cmd, args.join(" "));
  const result = spawnSync(cmd, args, { stdio: "inherit", shell: false });
  if (result.status !== 0) failed = true;
}

if (failed) {
  console.log("\nCONTROLLED_LIVE_ACTIVATION_CHECK_FAILED");
  process.exit(1);
}

console.log("\nCONTROLLED_LIVE_ACTIVATION_CHECK_PASSED");
