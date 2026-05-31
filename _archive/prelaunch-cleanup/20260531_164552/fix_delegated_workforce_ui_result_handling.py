from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
admin_file = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"

backup_dir = ROOT / "backups" / f"delegated_workforce_ui_result_handling_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(admin_file, backup_dir / admin_file.name)

content = admin_file.read_text(encoding="utf-8")

old = """      if (!result?.success) {
        showToast("Delegated workforce execution needs review.");
        return;
      }

      setDelegatedWorkforceResults((prev) => [result, ...prev].slice(0, 10));
      await loadActionExecutionHistory();
      showToast(`Delegated workforce completed ${result.completed_count || 0} packet(s), blocked ${result.blocked_count || 0}.`);
"""

new = """      if (!result?.success) {
        setDelegatedWorkforceResults((prev) => [result, ...prev].slice(0, 10));
        await loadActionExecutionHistory();
        showToast("Delegated workforce execution returned review status.");
        return;
      }

      const completedCount = Number(result.completed_count || 0);
      const queuedCount = Number(result.queued_count || 0);
      const blockedCount = Number(result.blocked_count || 0);
      const performedCount = (result.completed_results || []).filter((item: any) => item?.performed_actual_action === true).length;

      setDelegatedWorkforceResults((prev) => [result, ...prev].slice(0, 10));
      await loadActionExecutionHistory();

      if (performedCount > 0) {
        showToast(`Delegated workforce executed ${performedCount} action(s). Queued ${queuedCount}, blocked ${blockedCount}.`);
      } else if (queuedCount > 0 || blockedCount > 0) {
        showToast(`Delegated workforce needs review. Queued ${queuedCount}, blocked ${blockedCount}.`);
      } else {
        showToast(`Delegated workforce completed ${completedCount} packet(s).`);
      }
"""

if old not in content:
    raise SystemExit("DELEGATED_RESULT_HANDLING_BLOCK_NOT_FOUND")

content = content.replace(old, new)

test_marker = """{delegatedWorkforceResults.length ? delegatedWorkforceResults.slice(0, 5).map((result: any, index: number) => ("""

if "performed_actual_action" not in content[content.find("delegatedWorkforceResults") : content.find("delegatedWorkforceResults") + 8000]:
    print("WARNING: delegated result render may still need visual expansion later")

admin_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_delegated_workforce_ui_result_handling.py"
test_file.write_text(r'''
from pathlib import Path

p = Path("frontend/src/app/admin/page.tsx")
text = p.read_text(encoding="utf-8")

assert "performedCount" in text
assert "performed_actual_action" in text
assert "Delegated workforce executed" in text
assert "Queued ${queuedCount}, blocked ${blockedCount}" in text
assert "loadActionExecutionHistory" in text

print("DELEGATED_WORKFORCE_UI_RESULT_HANDLING_TEST_PASSED")
''', encoding="utf-8")

print("DELEGATED_WORKFORCE_UI_RESULT_HANDLING_FIXED")
print(f"Backup: {backup_dir}")
print(f"Updated: {admin_file}")
print(f"Created: {test_file}")