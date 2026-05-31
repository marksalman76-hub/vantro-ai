const { spawnSync } = require("child_process");

const result = spawnSync(
  "python",
  ["scripts/activation/controlled-openai-live-execution.py"],
  { stdio: "inherit", shell: false }
);

if (result.status !== 0) {
  console.log("CONTROLLED_OPENAI_LIVE_EXECUTION_CHECK_FAILED");
  process.exit(1);
}

console.log("CONTROLLED_OPENAI_LIVE_EXECUTION_CHECK_PASSED");
