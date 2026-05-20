from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_execution_timeline_cards_{timestamp}.tsx"
backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

text = path.read_text(encoding="utf-8")

old = '''              {(executionTimeline.length
                ? executionTimeline.map((event) => [
                    event.created_at
                      ? new Date(event.created_at).toLocaleString()
                      : "Live",
                    event.title || event.event_type || "Execution event",
                    getAgentDisplayName(event.agent_id || "agent"),
                  ])
                : [
                    [
                      liveDeliverable?.created_at || "Live",
                      liveDeliverable
                        ? "Deliverable generated"
                        : timelineLoading
                          ? "Loading execution timeline"
                          : "Waiting for execution",
                      selectedAgents.length
                        ? getAgentDisplayName(selectedAgents[0])
                        : "Selected agent",
                    ],
                  ]).map(([time, event, actor]) => (
                <div
                  key={event}
                  style={{
                    display: "grid",
                    gridTemplateColumns: "minmax(70px,90px) minmax(140px,1fr) auto",
                    gap: 14,
                    alignItems: "center",
                    borderBottom: "1px solid #eef2f7",
                    paddingBottom: 13,
                  }}
                >
                  <div style={{ color: "#64748b", fontSize: 13 }}>● {time}</div>
                  <div style={{ fontWeight: 850 }}>{event}</div>
                  <div style={{ color: "#64748b", fontSize: 13 }}>{actor}</div>
                </div>
              ))}'''

new = '''              {(executionTimeline.length
                ? executionTimeline
                : [{
                    event_id: "pending_execution_timeline",
                    created_at: liveDeliverable?.created_at || "",
                    agent_id: selectedAgents[0] || "agent",
                    event_type: timelineLoading ? "loading_execution_timeline" : "waiting_for_execution",
                    event_status: liveDeliverable ? "deliverable_generated" : "waiting",
                    workflow_stage: "client_workspace",
                    action_type: "client_execution",
                    title: liveDeliverable
                      ? "Deliverable generated"
                      : timelineLoading
                        ? "Loading execution timeline"
                        : "Waiting for execution",
                    summary: liveDeliverable
                      ? "The latest client deliverable is ready for review."
                      : "Run selected agents to generate live governed execution events.",
                    approval_status: reviewStatus,
                    quality_status: liveDeliverable ? "ready_for_review" : "pending",
                    execution_status: executionState,
                  }]).map((event) => {
                const time = event.created_at
                  ? new Date(event.created_at).toLocaleString()
                  : "Live";
                const agentName = getAgentDisplayName(event.agent_id || "agent");
                const approvalStatus = event.approval_status || "not_required";
                const qualityStatus = event.quality_status || "pending";
                const executionStatus = event.execution_status || event.event_status || "tracked";

                return (
                  <div
                    key={event.event_id || `${event.agent_id}-${event.event_type}`}
                    style={{
                      border: "1px solid #e5eaf2",
                      borderRadius: 18,
                      padding: 16,
                      background: "#ffffff",
                      boxShadow: "0 12px 30px rgba(15,23,42,0.05)",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 14, flexWrap: "wrap", alignItems: "flex-start" }}>
                      <div>
                        <div style={{ color: "#64748b", fontSize: 12.5, fontWeight: 800 }}>{time}</div>
                        <div style={{ fontWeight: 950, color: "#0f172a", fontSize: 16, marginTop: 5 }}>
                          {event.title || event.event_type || "Execution event"}
                        </div>
                        <div style={{ color: "#475569", fontSize: 13.5, lineHeight: 1.45, marginTop: 6 }}>
                          {event.summary || "Governed execution event recorded by the platform ledger."}
                        </div>
                      </div>

                      <div style={{ textAlign: "right", color: "#64748b", fontSize: 13, fontWeight: 850 }}>
                        {agentName}
                      </div>
                    </div>

                    <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 14 }}>
                      <span style={{ background: "#eff6ff", color: "#2563eb", border: "1px solid #dbeafe", borderRadius: 999, padding: "7px 10px", fontWeight: 850, fontSize: 12 }}>
                        {event.execution_action || event.action_type || "Tracked action"}
                      </span>
                      <span style={{ background: "#f0fdf4", color: "#16a34a", border: "1px solid #dcfce7", borderRadius: 999, padding: "7px 10px", fontWeight: 850, fontSize: 12 }}>
                        Quality: {qualityStatus}
                      </span>
                      <span style={{ background: "#fff7ed", color: "#ea580c", border: "1px solid #fed7aa", borderRadius: 999, padding: "7px 10px", fontWeight: 850, fontSize: 12 }}>
                        Approval: {approvalStatus}
                      </span>
                      <span style={{ background: "#f8fafc", color: "#334155", border: "1px solid #e2e8f0", borderRadius: 999, padding: "7px 10px", fontWeight: 850, fontSize: 12 }}>
                        Execution: {executionStatus}
                      </span>
                    </div>
                  </div>
                );
              })}'''

if old not in text:
    raise RuntimeError("Timeline block not found")

path.write_text(text.replace(old, new), encoding="utf-8")

print("CLIENT_EXECUTION_TIMELINE_CARDS_UPGRADED")
print(f"Backup: {backup}")