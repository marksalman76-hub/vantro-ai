
from pathlib import Path

security = Path("backend/app/core/security_audit_enforcement_runtime.py").read_text(encoding="utf-8")
durable = Path("backend/app/runtime/durable_external_action_records.py").read_text(encoding="utf-8")
gitignore = Path(".gitignore").read_text(encoding="utf-8")

assert "ADMIN_EVIDENCE_PROXY_PATHS" in security
assert "admin-execution-evidence" in security
assert "DEFAULT_TRUSTED_ORIGINS" in security
assert "CREATE TABLE IF NOT EXISTS external_action_records" in durable
assert "persistence_mode" in durable
assert "DATABASE_URL" in durable
assert "runtime_data/*.jsonl" in gitignore
assert "Beta functional stabilisation scratch files" in gitignore

print("BETA_FUNCTIONAL_STABILISATION_TEST_PASSED")
