from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
page = ROOT / "frontend" / "src" / "app" / "admin" / "live-execution" / "page.tsx"

backup_dir = ROOT / "backups" / f"admin_live_execution_dynamic_output_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(page, backup_dir / "page.tsx")

s = page.read_text(encoding="utf-8")

s = s.replace(
'''              <div style={{ display: "flex", justifyContent: "space-between", gap: 14 }}>
                <h3 style={{ fontSize: 24, margin: 0 }}>{completed ? "Live admin execution deliverable" : "Ready for execution"}</h3>
                <span style={{ color: "#a8b3cf" }}>{completed ? "Ready for review" : "Waiting"}</span>
              </div>
              <p style={{ color: "#cbd5e1", fontSize: 20, lineHeight: 1.45 }}>
                {completed
                  ? "A live governed admin deliverable has been generated from the selected AI agent."
                  : "Run an agent to generate a live governed admin deliverable."}
              </p>''',
'''              <div style={{ display: "flex", justifyContent: "space-between", gap: 14 }}>
                <h3 style={{ fontSize: 24, margin: 0 }}>
                  {completed
                    ? `${AGENTS.find(([id]) => id === agent)?.[1] || agent} live output`
                    : running
                      ? "Execution running"
                      : "Ready for execution"}
                </h3>
                <span style={{ color: "#a8b3cf" }}>
                  {completed ? "Ready for review" : running ? "Generating" : "Waiting"}
                </span>
              </div>
              <p style={{ color: "#cbd5e1", fontSize: 20, lineHeight: 1.45 }}>
                {completed && outputText
                  ? outputText.slice(0, 260) + (outputText.length > 260 ? "..." : "")
                  : running
                    ? "Live governed execution is running. The generated output will appear here as soon as the provider response completes."
                    : "Run an agent to generate a live governed admin deliverable."}
              </p>'''
)

s = s.replace(
'''                {outputText || "Generated deliverable output will appear here after execution."}''',
'''                {running
                  ? "Generating live governed output..."
                  : outputText || "Generated deliverable output will appear here after execution."}'''
)

s = s.replace(
'''                  ["Provider", adapter?.provider_key || "—"],
                  ["Latency", adapter?.latency_ms ? `${adapter.latency_ms}ms` : "—"],
                  ["Memory", result?.memory?.memory_saved ? "Saved" : "—"],
                  ["Safe", adapter?.customer_safe ? "True" : "—"],''',
'''                  ["Provider", adapter?.provider_key || (running ? "Running" : "—")],
                  ["Latency", adapter?.latency_ms ? `${adapter.latency_ms}ms` : running ? "Measuring" : "—"],
                  ["Memory", result?.memory?.memory_saved ? "Saved" : running ? "Pending" : "—"],
                  ["Safe", adapter?.customer_safe ? "True" : running ? "Pending" : "—"],'''
)

page.write_text(s, encoding="utf-8")

print("ADMIN_LIVE_EXECUTION_DYNAMIC_OUTPUT_FIXED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {page}")