
from pathlib import Path

p = Path("frontend/src/app/admin/page.tsx")
text = p.read_text(encoding="utf-8")

assert "Persistent Action History" in text
assert "loadActionExecutionHistory" in text
assert "/api/action-execution-history?tenant_id=owner_admin&limit=10" in text
assert "actionExecutionHistory" in text
assert "actions_performed" in text

print("ADMIN_ACTION_HISTORY_PANEL_TEST_PASSED")
