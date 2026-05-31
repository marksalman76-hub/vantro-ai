from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "admin" / "page.tsx"

backup_dir = root / "backups" / f"admin_run_agent_targeted_safe_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "page.tsx")

text = target.read_text(encoding="utf-8")

start = text.find("async function runAdminAgent()")
end = text.find("async function callDeploymentControl", start)

if start == -1 or end == -1:
    raise SystemExit("Could not isolate runAdminAgent function.")

old_function = text[start:end]

new_function = r'''async function runAdminAgent() {
    if (selectedRun.length === 0 || !task.trim()) {
      setRunResult({ success: false, message: "Select at least one agent and enter a task." });
      showToast("Select at least one agent and enter a task.");
      return;
    }

    setRunning(true);
    setRunResult(null);

    try {
      const results = [];

      for (const agentId of selectedRun) {
        const payload = {
          account_reference: "owner_admin",
          requested_agent: agentId,
          workflow_stage: "admin_internal_execution",
          action_type: "admin_owner_execution",
          actor_role: "owner",
          owner_approved: true,
          admin_execution: true,
          bypass_client_credits: true,
          task,
        };

        const response = await fetch("/api/admin-deployment-control", {
          method: "POST",
          cache: "no-store",
          headers: {
            "Content-Type": "application/json",
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
          },
          body: JSON.stringify({
            path: "/run-agent",
            method: "POST",
            payload,
          }),
        });

        const data = await response.json().catch(() => ({
          success: false,
          message: "Invalid admin execution response.",
        }));

        results.push({
          agent_id: agentId,
          http_status: response.status,
          success: data?.success === true,
          status:
            data?.workflow_status ||
            data?.execution_status ||
            data?.status ||
            data?.error ||
            "completed",
          message:
            data?.message ||
            data?.summary ||
            data?.error ||
            "Execution response received.",
        });
      }

      const allSucceeded = results.every((item) => item.success === true);

      setRunResult({
        success: allSucceeded,
        status: allSucceeded
          ? "Admin execution completed"
          : "Admin execution needs review",
        selected_agent_count: selectedRun.length,
        results,
      });

      showToast(allSucceeded ? "Selected agents completed." : "Some agent runs need review.");
    } catch {
      setRunResult({ success: false, message: "Admin execution failed." });
      showToast("Admin execution failed.");
    } finally {
      setRunning(false);
    }
  }

  '''

text = text[:start] + new_function + text[end:]

old_output = '''              <pre className={runResult ? "output has" : "output"}>
                {runResult ? JSON.stringify(runResult, null, 2) : "Agent output will appear here..."}
              </pre>'''

new_output = '''              <div className={runResult ? "output has" : "output"}>
                {!runResult ? (
                  "Agent output will appear here..."
                ) : (
                  <div className="adminResultCard">
                    <strong>{runResult?.status || "Execution result"}</strong>
                    <p>
                      {runResult?.message ||
                        `${runResult?.selected_agent_count || 0} selected agent run(s) processed.`}
                    </p>

                    {Array.isArray(runResult?.results) ? (
                      <div className="resultList">
                        {runResult.results.map((item: any, index: number) => (
                          <div className="resultRow" key={index}>
                            <span>{item?.agent_id || "agent"}</span>
                            <b>{item?.success ? "SUCCESS" : "REVIEW"}</b>
                            <small>{item?.message || item?.status || "Processed"}</small>
                          </div>
                        ))}
                      </div>
                    ) : null}
                  </div>
                )}
              </div>'''

if old_output not in text:
    raise SystemExit("Could not find raw JSON output block.")

text = text.replace(old_output, new_output, 1)

if "JSON.stringify(runResult" in text:
    raise SystemExit("Raw runResult JSON output still present.")

target.write_text(text, encoding="utf-8")

print("ADMIN_RUN_AGENT_TARGETED_SAFE_PATCHED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")