from pathlib import Path

text = Path("backend/app/main.py").read_text(encoding="utf-8")

assert "local_runtime_regression_bypass" in text
assert "ALLOW_LOCAL_RUNTIME_BYPASS" in text
assert "local_runtime_regression_test_guard" in text

print("RUN_AGENT_REGRESSION_TEST_CREDIT_BYPASS_TESTS_PASSED")
print("regression_bypass_present", "local_runtime_regression_bypass" in text)
print("env_guard_present", "ALLOW_LOCAL_RUNTIME_BYPASS" in text)
