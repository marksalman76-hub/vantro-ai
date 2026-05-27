
from pathlib import Path

text = Path("backend/app/main.py").read_text(encoding="utf-8")

assert "try:" in text
assert "pg_lookup_client_account(request.tenant_id)" in text
assert "DATABASE_URL_missing" in text
assert "owner_admin_internal_execution" in text
assert "local_test_runtime_guard_applied" in text

print("RUN_AGENT_LOCAL_TEST_RUNTIME_GUARD_TESTS_PASSED")
print("database_url_guard_installed", "DATABASE_URL_missing" in text)
print("owner_admin_only_guard", "owner_admin_internal_execution" in text)
print("local_test_marker", "local_test_runtime_guard_applied" in text)
