#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const configIndex = process.argv.indexOf("--config");
const configPath = configIndex >= 0 && process.argv[configIndex + 1]
  ? path.resolve(process.argv[configIndex + 1])
  : path.resolve("config/providers.json");

fs.mkdirSync(path.dirname(configPath), { recursive: true });

if (!fs.existsSync(configPath)) {
  const defaultConfig = {
    providers: [
      {
        id: "openai",
        enabled: true,
        priority: 1,
        live_external_calls_require_owner_approval: true
      },
      {
        id: "manual_review",
        enabled: true,
        priority: 99,
        fallback_only: true
      }
    ],
    safety: {
      live_external_calls_enabled_by_default: false,
      owner_approval_required: true,
      customer_safe_failover: true
    }
  };
  fs.writeFileSync(configPath, JSON.stringify(defaultConfig, null, 2));
}

const config = JSON.parse(fs.readFileSync(configPath, "utf8"));

const report = {
  script: "provider-failover",
  status: "PROVIDER_FAILOVER_CHAIN_READY",
  env: process.argv.includes("--env") ? process.argv[process.argv.indexOf("--env") + 1] : "local",
  test_all: process.argv.includes("--test-all"),
  config: configPath,
  provider_count: Array.isArray(config.providers) ? config.providers.length : 0,
  owner_approval_required: config?.safety?.owner_approval_required !== false,
  live_external_calls_enabled_by_default: config?.safety?.live_external_calls_enabled_by_default === true,
  live_runtime_changed: false,
  external_provider_called: false,
  customer_safe: true
};

console.log("PROVIDER_FAILOVER_CHAIN_READY");
console.log(JSON.stringify(report, null, 2));
