from pathlib import Path

s = Path("backend/app/main.py").read_text(encoding="utf-8")

assert "account_lookup_bypassed" in s
assert "local_runtime_regression_bypass" in s
assert "owner_admin_internal_bypass" in s
assert "except RuntimeError as exc:\n    except RuntimeError as exc:" not in s

print("FIX_RUN_AGENT_ACCOUNT_LOOKUP_GUARD_INDENT_TESTS_PASSED")
print("account_lookup_guard_clean", "account_lookup_bypassed" in s)
