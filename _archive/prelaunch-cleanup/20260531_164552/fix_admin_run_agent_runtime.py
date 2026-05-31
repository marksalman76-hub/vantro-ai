from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()

target = root / "frontend" / "src" / "app" / "admin" / "page.tsx"

backup_dir = root / "backups" / f"admin_run_agent_runtime_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

shutil.copy2(target, backup_dir / "page.tsx")

text = target.read_text(encoding="utf-8")

old_fetch = '''      const response = await fetch("/api/run-agent", {'''

new_fetch = '''      const response = await fetch("/api/admin-deployment-control", {'''

if old_fetch not in text:
    raise SystemExit("Could not find direct run-agent fetch.")

text = text.replace(old_fetch, new_fetch, 1)

text = text.replace(
'''        headers: {
          "Content-Type": "application/json",
        },''',

'''        headers: {
          "Content-Type": "application/json",
          "x-actor-role": "owner",
          "x-tenant-id": "owner",
        },'''
)

text = text.replace(
'''        body: JSON.stringify({''',

'''        body: JSON.stringify({
          path: "/run-agent",
          method: "POST",
          payload: {'''
)

text = text.replace(
'''          task,
        }),''',

'''          task,
          },
        }),'''
)

old_output = '''              <pre className={runResult ? "output has" : "output"}>
                {runResult ? JSON.stringify(runResult, null, 2) : "Agent output will appear here..."}
              </pre>'''

new_output = '''              <div className={runResult ? "output has" : "output"}>
                {!runResult ? (
                  "Agent output will appear here..."
                ) : (
                  <div className="adminResultCard">
                    <strong>
                      {runResult?.success === false
                        ? "Execution blocked or failed"
                        : "Execution completed"}
                    </strong>

                    <p>
                      {runResult?.message ||
                        runResult?.status ||
                        "Execution finished."}
                    </p>

                    {Array.isArray(runResult?.results) ? (
                      <div className="resultList">
                        {runResult.results.map((item: any, index: number) => (
                          <div className="resultRow" key={index}>
                            <span>{item?.agent_id || "agent"}</span>
                            <b>
                              {item?.http_status === 200
                                ? "SUCCESS"
                                : item?.http_status || "CHECK"}
                            </b>
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

target.write_text(text, encoding="utf-8")

print("ADMIN_RUN_AGENT_RUNTIME_FIXED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")