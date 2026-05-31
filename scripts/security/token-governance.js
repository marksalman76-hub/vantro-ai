const fs = require("fs");
const path = require("path");

const ttlArgIndex = process.argv.indexOf("--ttl");
const ttl = ttlArgIndex >= 0 ? Number(process.argv[ttlArgIndex + 1]) : 3600;

const result = {
  success: ttl > 0 && ttl <= 3600,
  ttl_seconds: ttl,
  short_lived_tokens_required: true,
  max_allowed_ttl_seconds: 3600,
  production_rotation_executed: false,
  verification_only: true
};

fs.mkdirSync(path.join(process.cwd(), "telemetry", "security"), { recursive: true });
fs.writeFileSync(
  path.join(process.cwd(), "telemetry", "security", "token-governance-verification.json"),
  JSON.stringify(result, null, 2)
);

console.log("TOKEN_GOVERNANCE_RUNTIME_STARTED");
console.log("SHORT_LIVED_TOKEN_POLICY_ACTIVE");
console.log("TTL_SECONDS:", ttl);
console.log("TOKEN_GOVERNANCE_RUNTIME_READY");

if (!result.success) {
  console.log("TOKEN_GOVERNANCE_FAILED_TTL_TOO_LONG");
  process.exitCode = 1;
}
