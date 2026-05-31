const { spawnSync } = require("child_process");

const commands = [
  ["python", ["scripts/activation/live-production-provisioning-verifier.py"]],
  ["python", ["scripts/activation/final-live-activation-verifier.py"]]
];

let failed = false;

for (const [cmd, args] of commands) {
  console.log("\nRUNNING:", cmd, args.join(" "));
  const result = spawnSync(cmd, args, { stdio: "inherit", shell: false });
  if (result.status !== 0) failed = true;
}

if (failed) {
  console.log("\nLIVE_PRODUCTION_PROVISIONING_CHECK_FAILED");
  process.exit(1);
}

console.log("\nLIVE_PRODUCTION_PROVISIONING_CHECK_PASSED");
