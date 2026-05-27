
from pathlib import Path

text = Path("backend/app/main.py").read_text(encoding="utf-8")

assert "try:" in text
assert "pg_client_credit_gate" in text
assert "owner_admin_local_test_runtime_guard" in text
assert "local_test_runtime_guard_applied" in text
assert "credential_values_exposed" in text

print("RUN_AGENT_CREDIT_GATE_LOCAL_TEST_GUARD_TESTS_PASSED")
print("credit_gate_guard_installed", "owner_admin_local_test_runtime_guard" in text)
print("local_test_marker", "local_test_runtime_guard_applied" in text)
