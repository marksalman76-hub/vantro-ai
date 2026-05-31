const fs = require("fs");
const path = require("path");

const outputDir = path.join(process.cwd(), "docs", "runbooks");

if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

const content = `
# Incident Recovery Runbook

## Emergency Actions
- Pause provider execution
- Activate fallback providers
- Disable unsafe runtime
- Restore latest backup
`;

fs.writeFileSync(
    path.join(outputDir, "incident-recovery.md"),
    content
);

console.log("RUNBOOKS_GENERATED");
