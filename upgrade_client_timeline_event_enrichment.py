from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_timeline_event_enrichment_{timestamp}.tsx"
backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

text = path.read_text(encoding="utf-8")

text = text.replace(
'''                const approvalStatus = event.approval_status || "not_required";
                const qualityStatus = event.quality_status || "pending";
                const executionStatus = event.execution_status || event.event_status || "tracked";''',
'''                const approvalStatus = event.approval_status || "not_required";
                const qualityStatus = event.quality_status || "pending";
                const executionStatus = event.execution_status || event.event_status || "tracked";
                const isExecutionIssue = String(executionStatus).toLowerCase().includes("failed") || String(executionStatus).toLowerCase().includes("unsupported");
                const isApprovalRequired = String(approvalStatus).toLowerCase().includes("approval") && !String(approvalStatus).toLowerCase().includes("approved_safe");
                const statusTone = isExecutionIssue
                  ? { bg: "#fff7ed", border: "#fed7aa", text: "#ea580c", label: "Needs attention" }
                  : isApprovalRequired
                    ? { bg: "#fffbeb", border: "#fde68a", text: "#ca8a04", label: "Approval gated" }
                    : { bg: "#f0fdf4", border: "#bbf7d0", text: "#16a34a", label: "Governed ready" };'''
)

text = text.replace(
'''                      border: "1px solid #e5eaf2",
                      borderRadius: 18,
                      padding: 16,
                      background: "#ffffff",
                      boxShadow: "0 12px 30px rgba(15,23,42,0.05)",''',
'''                      border: `1px solid ${statusTone.border}`,
                      borderRadius: 18,
                      padding: 16,
                      background: "#ffffff",
                      boxShadow: "0 12px 30px rgba(15,23,42,0.05)",'''
)

text = text.replace(
'''                      <div style={{ textAlign: "right", color: "#64748b", fontSize: 13, fontWeight: 850 }}>
                        {agentName}
                      </div>''',
'''                      <div style={{ textAlign: "right", color: "#64748b", fontSize: 13, fontWeight: 850 }}>
                        <div>{agentName}</div>
                        <div style={{ marginTop: 8, display: "inline-flex", background: statusTone.bg, color: statusTone.text, border: `1px solid ${statusTone.border}`, borderRadius: 999, padding: "6px 9px", fontSize: 11.5, fontWeight: 950 }}>
                          {statusTone.label}
                        </div>
                      </div>'''
)

text = text.replace(
'''                      <span style={{ background: "#f8fafc", color: "#334155", border: "1px solid #e2e8f0", borderRadius: 999, padding: "7px 10px", fontWeight: 850, fontSize: 12 }}>
                        Execution: {executionStatus}
                      </span>''',
'''                      <span style={{ background: statusTone.bg, color: statusTone.text, border: `1px solid ${statusTone.border}`, borderRadius: 999, padding: "7px 10px", fontWeight: 850, fontSize: 12 }}>
                        Execution: {executionStatus}
                      </span>
                      <span style={{ background: "#f8fafc", color: "#334155", border: "1px solid #e2e8f0", borderRadius: 999, padding: "7px 10px", fontWeight: 850, fontSize: 12 }}>
                        Stage: {event.workflow_stage || "workflow"}
                      </span>'''
)

path.write_text(text, encoding="utf-8")

print("CLIENT_TIMELINE_EVENT_ENRICHMENT_UPGRADED")
print(f"Backup: {backup}")