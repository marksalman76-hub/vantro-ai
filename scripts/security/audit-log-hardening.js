const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const logDir = path.join(process.cwd(), "logs");
const telemetryDir = path.join(process.cwd(), "telemetry", "security");
fs.mkdirSync(logDir, { recursive: true });
fs.mkdirSync(telemetryDir, { recursive: true });

const auditFile = path.join(logDir, "immutable-audit.log");
const chainFile = path.join(telemetryDir, "audit-hash-chain.json");

if (!fs.existsSync(auditFile)) fs.writeFileSync(auditFile, "");

let chain = [];
if (fs.existsSync(chainFile)) {
  chain = JSON.parse(fs.readFileSync(chainFile, "utf8"));
}

const previousHash = chain.length ? chain[chain.length - 1].entry_hash : "GENESIS";
const entry = {
  timestamp: new Date().toISOString(),
  event: "APPEND_ONLY_AUDIT_TAMPER_EVIDENCE_CHECKPOINT",
  previous_hash: previousHash
};

const entryHash = crypto
  .createHash("sha256")
  .update(JSON.stringify(entry))
  .digest("hex");

entry.entry_hash = entryHash;
chain.push(entry);

fs.appendFileSync(auditFile, `[${entry.timestamp}] ${entry.event} hash=${entryHash} prev=${previousHash}\n`);
fs.writeFileSync(chainFile, JSON.stringify(chain, null, 2));

console.log("AUDIT_LOG_IMMUTABILITY_ENABLED");
console.log("TAMPER_EVIDENCE_HASH_CHAIN_ACTIVE");
console.log("LATEST_HASH:", entryHash);
