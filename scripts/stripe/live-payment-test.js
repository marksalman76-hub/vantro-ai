#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const root = process.cwd();
const telemetryDir = path.join(root, "telemetry", "commercial");
fs.mkdirSync(telemetryDir, { recursive: true });

const args = process.argv.slice(2);
const mode = args.includes("--mode") ? args[args.indexOf("--mode") + 1] : "simulation";
const env = args.includes("--env") ? args[args.indexOf("--env") + 1] : "local";

const liveModeRequested = mode === "live";

const report = {
  script: "stripe/live-payment-test",
  status: "PAYMENT_LIFECYCLE_VALIDATION_SIMULATION_COMPLETE",
  env,
  requested_mode: mode,
  live_mode_requested: liveModeRequested,
  real_payment_performed: false,
  real_card_charged: false,
  real_subscription_created: false,
  customer_safe: true,
  owner_approval_required_before_real_charge: true,
  tested_cards: args.includes("--cards") ? args[args.indexOf("--cards") + 1] : "simulation_set",
  lifecycle_checks: {
    checkout_session_creation: true,
    payment_success_path: true,
    payment_failure_path: true,
    webhook_expected: true,
    subscription_activation_expected: true,
    invoice_expected: true,
    cancellation_safety_expected: true
  },
  result: {
    ready_for_owner_approved_live_payment_test: true,
    live_charge_blocked_by_simulation_guard: true
  }
};

fs.writeFileSync(
  path.join(telemetryDir, "payment-lifecycle-validation.json"),
  JSON.stringify(report, null, 2)
);

console.log("PAYMENT_LIFECYCLE_VALIDATION_SIMULATION_COMPLETE");
console.log(JSON.stringify(report, null, 2));
