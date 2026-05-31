
from pathlib import Path

target = Path("frontend/src/app/api/action-execution-history/route.ts")
assert target.exists()

text = target.read_text(encoding="utf-8")
assert "/admin/action-execution-history" in text
assert "x-admin-token" in text
assert "x-actor-role" in text
assert "owner_admin" in text
assert "readiness" in text

print("FRONTEND_ACTION_EXECUTION_HISTORY_PROXY_EXISTS_TEST_PASSED")
