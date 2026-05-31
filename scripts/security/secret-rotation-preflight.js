const fs = require("fs");
const path = require("path");

const policyPath = path.join(process.cwd(), "config", "security", "secret-rotation-policy.json");
const policy = JSON.parse(fs.readFileSync(policyPath, "utf8"));

const result = {
  success: true,
  mode: "preflight_only",
  production_rotation_executed: false,
  owner_approval_required: true,
  rotate_targets: policy.rotate_targets,
  blocked_until: policy.blocked_until,
  next_allowed_action: "manual owner-approved production secret rotation"
};

fs.mkdirSync(path.join(process.cwd(), "telemetry", "security"), { recursive: true });
fs.writeFileSync(
  path.join(process.cwd(), "telemetry", "security", "secret-rotation-preflight.json"),
  JSON.stringify(result, null, 2)
);

console.log("SECRET_ROTATION_PREFLIGHT_READY");
console.log("PRODUCTION_ROTATION_EXECUTED:false");
console.log("OWNER_APPROVAL_REQUIRED:true");
