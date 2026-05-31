
from pathlib import Path

p = Path("frontend/src/app/admin/page.tsx")
text = p.read_text(encoding="utf-8")

assert "performedCount" in text
assert "performed_actual_action" in text
assert "Delegated workforce executed" in text
assert "Queued ${queuedCount}, blocked ${blockedCount}" in text
assert "loadActionExecutionHistory" in text

print("DELEGATED_WORKFORCE_UI_RESULT_HANDLING_TEST_PASSED")
