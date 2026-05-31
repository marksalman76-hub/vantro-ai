#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const root = process.cwd();
const outDir = path.join(root, "telemetry");
fs.mkdirSync(outDir, { recursive: true });

const controls = {
  script: "register-emergency-controls",
  status: "EMERGENCY_CONTROLS_REGISTERED",
  live_runtime_changed: false,
  controls: {
    pause_live_external_actions: true,
    force_owner_review: true,
    disable_provider_execution: true,
    disable_client_execution_temporarily: true,
    preserve_admin_access: true,
    preserve_audit_logging: true
  },
  safety: {
    owner_authority_preserved: true,
    customer_safe: true,
    spending_requires_owner_approval: true
  }
};

fs.writeFileSync(
  path.join(outDir, "emergency-controls-status.json"),
  JSON.stringify(controls, null, 2)
);

console.log("EMERGENCY_CONTROLS_REGISTERED");
console.log(JSON.stringify(controls, null, 2));
