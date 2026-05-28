from pathlib import Path

text = Path("backend/app/main.py").read_text(encoding="utf-8")

assert 'owner_admin_credit_bypass = actor_role in {"owner", "admin", "owner_admin", "system"}' in text
assert 'owner_admin_internal_execution = (request.actor_role or "").strip().lower() in {"owner", "admin", "owner_admin", "system"}' in text

print("RUN_AGENT_OWNER_ADMIN_CREDIT_BYPASS_TEST_PASSED")
