const fs = require("fs");
const path = require("path");

const policyPath = path.join(process.cwd(), "config", "security", "secret-rotation-policy.json");
const policy = JSON.parse(fs.readFileSync(policyPath, "utf8"));

const ledger = {
  generated_at: new Date().toISOString(),
  production_rotation_executed: false,
  owner_approval_required: true,
  rotation_targets: policy.rotate_targets.map((name) => ({
    name,
    owner_review_required: true,
    rotated: false,
    rollback_ready: false,
    storage_expected: "production host secret manager"
  }))
};

fs.mkdirSync(path.join(process.cwd(), "telemetry", "security"), { recursive: true });
fs.writeFileSync(
  path.join(process.cwd(), "telemetry", "security", "secret-inventory-ledger.json"),
  JSON.stringify(ledger, null, 2)
);

console.log("SECRET_INVENTORY_LEDGER_CREATED");
console.log("TARGETS:", ledger.rotation_targets.length);
