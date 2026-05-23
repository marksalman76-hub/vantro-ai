from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_final_compact_execution_replace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

start_marker = '        <section style={responsiveWorkspaceGridStyle}>'
title_marker = 'Select agents and launch governed execution.'

start = src.find(start_marker)
if start == -1:
    raise SystemExit("ERROR: responsiveWorkspaceGridStyle section not found.")

title_pos = src.find(title_marker, start)
if title_pos == -1:
    raise SystemExit("ERROR: Run AI Agent title not found inside responsiveWorkspaceGridStyle section.")

next_section = src.find('\n\n        <section', title_pos)
if next_section == -1:
    raise SystemExit("ERROR: Could not find end of top execution section.")

new_section = r'''        <section style={responsiveWorkspaceGridStyle}>
          <div style={{ ...cardStyle, minHeight: 470 }}>
            <StepHeader number="01" title="Run AI Agent" />
            <h3 style={cardTitle}>Select agents and launch governed execution.</h3>

            <div style={{ display: "grid", gridTemplateColumns: "245px minmax(0,1fr)", gap: 14, marginTop: 10 }}>
              <div>
                <div style={labelStyle}>Active agents</div>
                <div
                  style={{
                    display: "grid",
                    gap: 7,
                    maxHeight: 255,
                    overflowY: "auto",
                    paddingRight: 4,
                  }}
                >
                  {(account?.active_agents || DEFAULT_AGENTS).map((agent) => {
                    const active = selectedAgents.includes(agent);
                    return (
                      <button
                        key={getAgentDisplayName(agent)}
                        onClick={() => toggleAgent(agent)}
                        style={{
                          border: active ? "1px solid rgba(37, 99, 235, 0.38)" : "1px solid rgba(15, 23, 42, 0.10)",
                          background: active ? "linear-gradient(135deg,#eff6ff,#ffffff)" : "#ffffff",
                          color: active ? "var(--color-brand)" : "var(--color-dark)",
                          padding: "7px 9px",
                          borderRadius: 12,
                          cursor: "pointer",
                          textAlign: "left",
                          fontSize: 11.8,
                          fontWeight: 700,
                          transition: "all 0.18s ease",
                          boxShadow: active ? "0 10px 30px rgba(37,99,235,0.10)" : "0 1px 2px rgba(15,23,42,0.03)",
                        }}
                      >
                        {active ? "● " : "○ "}
                        {getAgentDisplayName(agent)}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <div style={labelStyle}>Task</div>
                <textarea
                  defaultValue="Create a client-specific client deliverable using the saved business profile, selected active agents, current offer, target audience, goals, and execution requirements."
                  style={{
                    width: "100%",
                    minHeight: 158,
                    resize: "none",
                    borderRadius: 16,
                    border: "1px solid #dbe3ee",
                    background: "#fff",
                    padding: 14,
                    fontSize: 11.8,
                    lineHeight: 1.42,
                    boxSizing: "border-box",
                    fontFamily: "inherit",
                  }}
                />

                <button
                  onClick={async () => {
                    setExecutionState("running");
                    setToastMessage("Execution started. Generating client deliverables...");

                    try {
                      const response = await fetch("/api/run-agent", {
                        method: "POST",
                        headers: { "Content-Type": "application/json", "x-tenant-id": tenantId, "x-actor-role": "customer" },
                        credentials: "include",
                        body: JSON.stringify({
                          selected_agents: selectedAgents,
                          task: "Create a client-specific client deliverable using the saved business profile, selected active agents, current offer, target audience, goals, and execution requirements.",
                          business_profile: {
                            niche: businessProfile.business_niche || "Saved client business profile",
                            target_audience: businessProfile.target_audience || "Saved target audience and customer context",
                            positioning: businessProfile.notes || "Client-specific commercial positioning and execution requirements",
                          },
                        }),
                      });

                      const data = await response.json();

                      if (!response.ok || !data?.success) {
                        throw new Error("Execution failed");
                      }

                      setLiveDeliverable(data.deliverable);
                      setSelectedAssetIndex(0);
                      setExecutionState("completed");
                      setReviewStatus("pending");
                      setToastMessage("Client deliverable generated and ready for review.");
                    } catch {
                      setExecutionState("idle");
                      setToastMessage("Execution could not be completed. Please try again.");
                    }
                  }}
                  style={{
                    marginTop: 12,
                    width: "100%",
                    border: "none",
                    borderRadius: 16,
                    background: executionState === "running" ? "linear-gradient(135deg,var(--color-muted),var(--color-mid))" : "linear-gradient(135deg,var(--color-brand),#06b6d4)",
                    color: "#fff",
                    padding: "13px 16px",
                    fontWeight: 760,
                    cursor: "pointer",
                    boxShadow: "0 12px 26px rgba(37,99,235,.18)",
                  }}
                >
                  {executionState === "running" ? "Generating..." : "✨ Run Agent"}
                </button>
              </div>
            </div>

            <div style={{ marginTop: 12, color: "var(--color-muted)", fontSize: 12 }}>
              ⓘ Runs use your saved business profile.
            </div>
          </div>

          <div style={{ ...cardStyle, minHeight: 470 }}>
            <StepHeader number="02" title="Live execution flow" />
            <h3 style={cardTitle}>Execution pipeline</h3>
            <p style={mutedText}>
              Every AI deliverable flows through approval, optimisation, workflow validation,
              and governed execution before deployment.
            </p>

            <div style={{ display: "grid", gap: 8, marginTop: 12 }}>
              {[
                ["Execution requested", executionState === "idle" ? "Waiting" : "Started", liveDeliverable?.created_at || "Live"],
                ["Business profile applied", "Context loaded", "Live"],
                ["Deliverable status", executionState === "completed" ? "Ready" : "Pending", liveDeliverable?.created_at || "Live"],
                ["Client review", reviewStatus === "approved" ? "Approved" : reviewStatus === "rejected" ? "Revision requested" : "Pending", reviewStatus === "approved" ? "Complete" : "Open"],
                ["Execution ready", "Next", "—"],
              ].map(([title, status, time], index) => (
                <div key={title} style={{ display: "grid", gridTemplateColumns: "30px 1fr auto", gap: 9, alignItems: "center" }}>
                  <div
                    style={{
                      width: 26,
                      height: 26,
                      minWidth: 26,
                      minHeight: 26,
                      borderRadius: "999px",
                      background: index === 4 ? "#06b6d4" : "var(--color-brand)",
                      color: "#fff",
                      display: "inline-flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 11,
                      fontWeight: 900,
                    }}
                  >
                    {index + 1}
                  </div>
                  <div
                    style={{
                      border: "1px solid #e5eaf2",
                      borderRadius: 12,
                      background: "#fff",
                      padding: "8px 10px",
                      boxShadow: "0 8px 20px rgba(15,23,42,.04)",
                    }}
                  >
                    <div style={{ fontWeight: 900, color: "var(--color-dark)", fontSize: 12 }}>{title}</div>
                    <div style={{ color: "var(--color-muted)", fontSize: 11.5, fontWeight: 800, marginTop: 2 }}>{status}</div>
                  </div>
                  <div style={{ color: "var(--color-muted)", fontSize: 11.5, fontWeight: 800 }}>{time}</div>
                </div>
              ))}

              <div
                style={{
                  border: "1px solid #dbeafe",
                  borderRadius: 14,
                  background: "linear-gradient(135deg,#eff6ff,#ffffff)",
                  padding: "9px 10px",
                  display: "grid",
                  gridTemplateColumns: "26px 1fr",
                  gap: 9,
                  alignItems: "center",
                }}
              >
                <div
                  style={{
                    width: 26,
                    height: 26,
                    borderRadius: 9,
                    background: "#ffffff",
                    color: "var(--color-brand)",
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontWeight: 900,
                    boxShadow: "0 4px 12px rgba(37,99,235,.08)",
                  }}
                >
                  ✦
                </div>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 900, color: "var(--color-dark)" }}>
                    Governed execution, every time.
                  </div>
                  <div style={{ marginTop: 2, fontSize: 11.5, fontWeight: 700, color: "var(--color-muted)", lineHeight: 1.35 }}>
                    Tracked, logged, quality-checked, and approval-routed.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>'''

src = src[:start] + new_section + src[next_section:]

# Remove any old detached governed strip if it remains after the replaced top section.
first = src.find("Governed execution, every time.")
second = src.find("Governed execution, every time.", first + 1)
if second != -1:
    old_start = src.rfind("<section", 0, second)
    old_end = src.find("</section>", second)
    if old_start != -1 and old_end != -1:
        src = src[:old_start] + src[old_end + len("</section>"):]

PAGE.write_text(src, encoding="utf-8")

print("FINAL_COMPACT_EXECUTION_SECTION_REPLACED")
print(f"Backup: {backup}")
print("Updated: frontend/src/app/client/page.tsx")
print("Business profile applied count:", src.count("Business profile applied"))
print("Governed strip count:", src.count("Governed execution, every time."))
print("Scrollable agent list installed:", "maxHeight: 255" in src and 'overflowY: "auto"' in src)