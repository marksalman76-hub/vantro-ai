#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const outputIndex = process.argv.indexOf("--output");
const outputDir = outputIndex >= 0 && process.argv[outputIndex + 1]
  ? path.resolve(process.argv[outputIndex + 1])
  : path.resolve("docs/runbooks");

fs.mkdirSync(outputDir, { recursive: true });

const runbooks = {
  "incident-response.md": `# Incident Response Runbook

## Scope
Production incident handling for the unique multi-agent platform.

## First actions
1. Confirm user-facing impact.
2. Check backend health.
3. Check frontend availability.
4. Check provider status.
5. Check recent deployments.
6. Pause live external actions if risk is detected.

## Owner-only controls
- Spending changes
- Provider activation
- Scaling decisions
- Customer-impacting emergency actions
`,

  "provider-failover.md": `# Provider Failover Runbook

## Trigger
Provider latency, failure rate, timeout, quota issue, or degraded generation quality.

## Response
1. Mark provider degraded.
2. Route eligible jobs to fallback provider.
3. Keep owner approval required for live external actions.
4. Preserve audit trail.
5. Notify owner before spend-impacting changes.
`,

  "backup-restore.md": `# Backup and Restore Runbook

## Verification
1. Confirm DATABASE_URL is configured in production.
2. Confirm backup snapshot availability.
3. Confirm restore verification process.
4. Never overwrite production without owner approval.

## Safety
Restore actions are approval-gated.
`
};

for (const [file, content] of Object.entries(runbooks)) {
  fs.writeFileSync(path.join(outputDir, file), content);
}

const report = {
  script: "generate-runbooks",
  status: "RUNBOOKS_GENERATED",
  output: outputDir,
  files: Object.keys(runbooks),
  live_runtime_changed: false
};

console.log("RUNBOOKS_GENERATED");
console.log(JSON.stringify(report, null, 2));
