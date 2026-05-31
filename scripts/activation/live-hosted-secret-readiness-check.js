const { spawnSync } = require("child_process");

const result = spawnSync(
  "python",
  ["scripts/activation/live-hosted-secret-readiness-verifier.py"],
  { stdio: "inherit", shell: false }
);

if (result.status !== 0) {
  console.log("LIVE_HOSTED_SECRET_READINESS_CHECK_FAILED");
  process.exit(1);
}

console.log("LIVE_HOSTED_SECRET_READINESS_CHECK_PASSED");
