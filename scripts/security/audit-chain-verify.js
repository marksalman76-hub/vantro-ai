const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const chainPath = path.join(process.cwd(), "telemetry", "security", "audit-hash-chain.json");

if (!fs.existsSync(chainPath)) {
  console.log("AUDIT_CHAIN_VERIFY_FAILED_MISSING_CHAIN");
  process.exit(1);
}

const chain = JSON.parse(fs.readFileSync(chainPath, "utf8"));
let previous = "GENESIS";
let ok = true;

for (const raw of chain) {
  const entry = { ...raw };
  const actualHash = entry.entry_hash;
  delete entry.entry_hash;

  const expectedHash = crypto
    .createHash("sha256")
    .update(JSON.stringify(entry))
    .digest("hex");

  if (entry.previous_hash !== previous || actualHash !== expectedHash) {
    ok = false;
    break;
  }

  previous = actualHash;
}

console.log("AUDIT_CHAIN_ENTRIES:", chain.length);
console.log(ok ? "AUDIT_CHAIN_VERIFY_PASSED" : "AUDIT_CHAIN_VERIFY_FAILED");

if (!ok) process.exit(1);
