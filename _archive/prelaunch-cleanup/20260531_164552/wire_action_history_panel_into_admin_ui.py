from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
admin_file = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"

backup_dir = ROOT / "backups" / f"admin_action_history_panel_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(admin_file, backup_dir / admin_file.name)

content = admin_file.read_text(encoding="utf-8")

old_state = """  const [delegatedWorkforceResults, setDelegatedWorkforceResults] = useState<any[]>([]);
"""
new_state = """  const [delegatedWorkforceResults, setDelegatedWorkforceResults] = useState<any[]>([]);
  const [actionExecutionHistory, setActionExecutionHistory] = useState<any[]>([]);
  const [actionHistorySummary, setActionHistorySummary] = useState<any>(null);
"""

if old_state not in content:
    raise SystemExit("STATE_MARKER_NOT_FOUND")
content = content.replace(old_state, new_state)

old_effect = """    loadOrchestrationDashboard();
  }, []);
"""
new_effect = """    loadOrchestrationDashboard();
    loadActionExecutionHistory();
  }, []);
"""

if old_effect not in content:
    raise SystemExit("EFFECT_MARKER_NOT_FOUND")
content = content.replace(old_effect, new_effect)

insert_after = """  async function loadOrchestrationDashboard() {
"""
function_block = """  async function loadActionExecutionHistory() {
    try {
      const response = await fetch("/api/action-execution-history?tenant_id=owner_admin&limit=10", {
        method: "GET",
        cache: "no-store",
      });
      const wrapper = await response.json();
      const data = wrapper?.data || wrapper;
      setActionExecutionHistory(data?.records || []);
      setActionHistorySummary(data);
    } catch {
      setActionExecutionHistory([]);
      setActionHistorySummary(null);
    }
  }

"""

if function_block not in content:
    if insert_after not in content:
        raise SystemExit("FUNCTION_INSERT_MARKER_NOT_FOUND")
    content = content.replace(insert_after, function_block + insert_after)

old_run_success = """      setDelegatedWorkforceResults((prev) => [result, ...prev].slice(0, 10));
      showToast(`Delegated workforce completed ${result.completed_count || 0} packet(s), blocked ${result.blocked_count || 0}.`);
"""
new_run_success = """      setDelegatedWorkforceResults((prev) => [result, ...prev].slice(0, 10));
      await loadActionExecutionHistory();
      showToast(`Delegated workforce completed ${result.completed_count || 0} packet(s), blocked ${result.blocked_count || 0}.`);
"""

if old_run_success not in content:
    raise SystemExit("RUN_SUCCESS_MARKER_NOT_FOUND")
content = content.replace(old_run_success, new_run_success)

panel_marker = """              <pre className={orchestrationResult ? "output has" : "output"}>
                {orchestrationResult ? JSON.stringify(orchestrationResult, null, 2) : "Orchestration test result will appear here..."}
              </pre>
            </Panel>
"""

history_panel = """              <pre className={orchestrationResult ? "output has" : "output"}>
                {orchestrationResult ? JSON.stringify(orchestrationResult, null, 2) : "Orchestration test result will appear here..."}
              </pre>
            </Panel>

            <Panel title="Persistent Action History" subtitle="Saved autonomous actions, adapter outputs, and customer-safe deliverables.">
              <div className="reviewRows">
                <div>
                  <span>Saved actions</span>
                  <b>{actionHistorySummary?.count ?? actionExecutionHistory.length}</b>
                </div>
                <div>
                  <span>Latest adapter</span>
                  <b>{actionExecutionHistory?.[0]?.adapter || "—"}</b>
                </div>
                <div>
                  <span>Actual actions</span>
                  <b>{actionExecutionHistory?.[0]?.performed_actual_action ? "Yes" : "—"}</b>
                </div>
              </div>

              <div className="reviewList">
                {actionExecutionHistory.length ? actionExecutionHistory.slice(0, 5).map((item: any, index: number) => (
                  <div className="reviewItem" key={item.history_id || index}>
                    <strong>{item.execution_status || "saved_action"}</strong>
                    <span>{String(item.assigned_agent || "agent").replaceAll("_", " ")} · {item.adapter || "adapter"}</span>
                    <p>
                      {(item.actions_performed || []).map((action: any) => action.type || action.status).filter(Boolean).join(" · ")
                        || item?.deliverable?.summary
                        || "Autonomous action record saved."}
                    </p>
                  </div>
                )) : (
                  <div className="reviewItem">
                    <strong>No action history loaded</strong>
                    <span>Run delegated workforce after deployment</span>
                    <p>Saved autonomous actions will appear here after execution.</p>
                  </div>
                )}
              </div>

              <button className="ghost full" onClick={loadActionExecutionHistory}>Refresh action history</button>
            </Panel>
"""

if panel_marker not in content:
    raise SystemExit("PANEL_INSERT_MARKER_NOT_FOUND")
content = content.replace(panel_marker, history_panel)

admin_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_admin_action_history_panel.py"
test_file.write_text(r'''
from pathlib import Path

p = Path("frontend/src/app/admin/page.tsx")
text = p.read_text(encoding="utf-8")

assert "Persistent Action History" in text
assert "loadActionExecutionHistory" in text
assert "/api/action-execution-history?tenant_id=owner_admin&limit=10" in text
assert "actionExecutionHistory" in text
assert "actions_performed" in text

print("ADMIN_ACTION_HISTORY_PANEL_TEST_PASSED")
''', encoding="utf-8")

print("ADMIN_ACTION_HISTORY_PANEL_WIRED")
print(f"Backup: {backup_dir}")
print(f"Updated: {admin_file}")
print(f"Created: {test_file}")