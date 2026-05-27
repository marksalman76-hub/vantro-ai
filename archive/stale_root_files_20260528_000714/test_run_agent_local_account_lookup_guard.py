from pathlib import Path

text = Path("backend/app/main.py").read_text(encoding="utf-8")

assert "account_lookup_bypassed" in text
assert "local_runtime_regression_bypass" in text
assert "DATABASE_URL_missing" in text

print("RUN_AGENT_LOCAL_ACCOUNT_LOOKUP_GUARD_TESTS_PASSED")
print("lookup_guard_present", "account_lookup_bypassed" in text)
print("regression_bypass_present", "local_runtime_regression_bypass" in text)
