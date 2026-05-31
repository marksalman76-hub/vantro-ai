from pathlib import Path
import json
import sys

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

from backend.app.core.secure_runtime_config import redact_text

samples = [
    "OPENAI key sk-1234567890abcdefghijklmnopqrstuv",
    "stripe whsec_1234567890abcdefghijklmnopqrstuv",
    "postgresql://user:password@example.com:5432/db",
    "ADMIN_PLATFORM_TOKEN=super-secret-token-value",
    "JWT_SECRET=super-secret-jwt-value",
    "DATABASE_URL=postgresql://user:pass@host:5432/db",
    {"ADMIN_PLATFORM_TOKEN": "super-secret-token-value"},
    {"JWT_SECRET": "super-secret-jwt-value"},
]

results = []
for sample in samples:
    rendered = json.dumps(sample) if isinstance(sample, dict) else sample
    redacted = redact_text(rendered)
    results.append({
        "input_contains_secret_shape": True,
        "output": redacted,
        "redacted": "[REDACTED_SECRET]" in redacted,
        "leaked_assignment_secret": "super-secret" in redacted,
    })

success = all(item["redacted"] and not item["leaked_assignment_secret"] for item in results)

report = {
    "success": success,
    "secret_values_exposed": False,
    "results": results,
}

out_dir = ROOT / "telemetry" / "security"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "redaction-verification.json").write_text(
    json.dumps(report, indent=2),
    encoding="utf-8",
)

print("REDACTION_VERIFICATION_COMPLETED")
print("REDACTION_SUCCESS:", success)

if not success:
    raise SystemExit(1)
