from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_activity_output_polish_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

start_marker = '        <section style={{ ...responsiveSecondaryGridStyle, alignItems: "stretch" }}>'
end_marker = '      {showEnterpriseCatalogueModal ? ('

start = src.find(start_marker)
end = src.find(end_marker, start)

if start == -1:
    raise SystemExit("ERROR: Activity/output section start not found.")
if end == -1:
    raise SystemExit("ERROR: Modal insertion point not found.")

new_section = r'''        <section style={{ ...responsiveSecondaryGridStyle, alignItems: "stretch" }}>
          <div style={{ ...cardStyle, minHeight: 360 }}>
            <StepHeader number="05" title="Activity" />
            <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: 14 }}>
              <div>
                <h3 style={cardTitle}>Activity</h3>
                <p style={{ ...mutedText, margin: "5px 0 0", color: "var(--color-brand)", fontWeight: 800 }}>
                  Latest governed activity
                </p>
              </div>
              <span
                style={{
                  background: "#ecfdf5",
                  color: "var(--color-teal)",
                  border: "1px solid #bbf7d0",
                  borderRadius: 999,
                  padding: "7px 10px",
                  fontSize: 11.5,
                  fontWeight: 900,
                  whiteSpace: "nowrap",
                }}
              >
                Live tracking
              </span>
            </div>

            <div style={{ display: "grid", gap: 10, marginTop: 16 }}>
              {[
                {
                  title: liveDeliverable ? "Deliverable generated" : "Ready for execution",
                  detail: liveDeliverable
                    ? "Latest client deliverable is ready for review."
                    : "Run selected agents to generate a new client deliverable.",
                  status: liveDeliverable ? "Ready for review" : "Waiting",
                  tone: liveDeliverable ? "#22c55e" : "var(--color-brand)",
                  icon: liveDeliverable ? "✓" : "→",
                },
                {
                  title: executionState === "completed" ? "Execution completed" : executionState === "running" ? "Execution running" : "Execution prepared",
                  detail: executionState === "running"
                    ? "Agent workflow is processing the current request."
                    : "Governed execution flow is prepared for the selected agents.",
                  status: executionState === "completed" ? "Completed" : executionState === "running" ? "Running" : "Prepared",
                  tone: executionState === "running" ? "#f59e0b" : "#06b6d4",
                  icon: executionState === "running" ? "…" : "⚡",
                },
                {
                  title: reviewStatus === "approved" ? "Client approved" : reviewStatus === "rejected" ? "Changes requested" : "Client review",
                  detail: reviewStatus === "approved"
                    ? "The deliverable has been approved."
                    : reviewStatus === "rejected"
                      ? "Feedback has been submitted for revision."
                      : "Approval controls are ready when the output is reviewed.",
                  status: reviewStatus === "approved" ? "Approved" : reviewStatus === "rejected" ? "Revision" : "Pending",
                  tone: reviewStatus === "rejected" ? "#ef4444" : "var(--color-brand)",
                  icon: reviewStatus === "approved" ? "✓" : reviewStatus === "rejected" ? "!" : "○",
                },
              ].map((item) => (
                <div
                  key={item.title}
                  style={{
                    border: "1px solid #e5eaf2",
                    borderRadius: 16,
                    background: "#fff",
                    padding: "12px 14px",
                    display: "grid",
                    gridTemplateColumns: "34px minmax(0,1fr) auto",
                    gap: 12,
                    alignItems: "center",
                    boxShadow: "0 8px 22px rgba(15,23,42,.035)",
                  }}
                >
                  <div
                    style={{
                      width: 32,
                      height: 32,
                      borderRadius: 12,
                      background: `${item.tone}18`,
                      color: item.tone,
                      display: "inline-flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontWeight: 950,
                    }}
                  >
                    {item.icon}
                  </div>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontSize: 13, fontWeight: 950, color: "var(--color-dark)" }}>{item.title}</div>
                    <div style={{ marginTop: 3, fontSize: 12, fontWeight: 700, color: "var(--color-muted)", lineHeight: 1.35 }}>
                      {item.detail}
                    </div>
                  </div>
                  <span
                    style={{
                      border: "1px solid #e5eaf2",
                      background: "#f8fafc",
                      borderRadius: 999,
                      padding: "6px 9px",
                      color: item.tone,
                      fontSize: 11.5,
                      fontWeight: 900,
                      whiteSpace: "nowrap",
                    }}
                  >
                    {item.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div style={{ ...cardStyle, minHeight: 360 }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start" }}>
              <div>
                <StepHeader number="06" title="Execution output viewer" />
                <h3 style={cardTitle}>Client deliverables</h3>
                <p style={{ ...mutedText, margin: "5px 0 0" }}>
                  Review the latest generated output and approve or request changes.
                </p>
              </div>
              <div
                style={{
                  background: reviewStatus === "rejected" ? "#fee2e2" : "#dcfce7",
                  color: reviewStatus === "rejected" ? "var(--color-red)" : "var(--color-teal)",
                  padding: "8px 12px",
                  borderRadius: 16,
                  fontWeight: 900,
                  fontSize: 11.8,
                  height: "fit-content",
                  whiteSpace: "nowrap",
                }}
              >
                {reviewStatus === "approved" ? "Approved" : reviewStatus === "rejected" ? "Revision requested" : "Ready for review"}
              </div>
            </div>

            <div
              style={{
                marginTop: 16,
                border: "1px solid #e5eaf2",
                borderRadius: 18,
                background: "#fff",
                padding: 14,
                display: "grid",
                gridTemplateColumns: "190px minmax(0,1fr)",
                gap: 16,
                alignItems: "stretch",
              }}
            >
              <div
                style={{
                  borderRadius: 16,
                  background: "linear-gradient(180deg,#f8fafc 0%,#ffffff 100%)",
                  border: "1px solid #e5eaf2",
                  minHeight: 190,
                  overflow: "hidden",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                {primaryAssetUrl ? (
                  <img
                    src={primaryAssetUrl}
                    alt={liveDeliverable?.title || "Generated deliverable asset"}
                    style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
                  />
                ) : (
                  <div style={{ textAlign: "center", padding: 18 }}>
                    <div style={{ fontSize: 28, marginBottom: 8 }}>🖼️</div>
                    <div style={{ fontWeight: 950, color: "var(--color-dark)", fontSize: 13 }}>No live asset attached</div>
                    <div style={{ marginTop: 6, fontSize: 11.5, color: "var(--color-muted)", fontWeight: 700, lineHeight: 1.35 }}>
                      Generated assets and previews will appear here automatically.
                    </div>
                  </div>
                )}
              </div>

              <div style={{ minWidth: 0, display: "flex", flexDirection: "column", justifyContent: "space-between", gap: 12 }}>
                <div>
                  <h4 style={{ margin: 0, fontSize: 20, letterSpacing: -0.3, color: "var(--color-dark)" }}>
                    {liveDeliverable?.title || "Live premium ecommerce launch campaign"}
                  </h4>
                  <p style={{ ...mutedText, margin: "6px 0 0", fontSize: 13 }}>
                    {liveDeliverable?.summary ||
                      "A client-ready campaign deliverable has been generated for the selected ecommerce task, including positioning, offer framing, conversion messaging, and execution-ready campaign direction."}
                  </p>

                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 12 }}>
                    {(liveDeliverable?.tags || ["Live output", getAgentDisplayName(selectedAgents[0] || "product_copywriting_agent"), "Approval required"]).slice(0, 4).map((tag) => (
                      <span
                        key={tag}
                        style={{
                          border: "1px solid #e5eaf2",
                          background: "#fff",
                          color: "var(--color-dark)",
                          borderRadius: 999,
                          padding: "7px 10px",
                          fontSize: 11.5,
                          fontWeight: 850,
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div style={{ display: "flex", gap: 9, flexWrap: "wrap", alignItems: "center" }}>
                  <button
                    type="button"
                    onClick={() => setShowDeliverableModal(true)}
                    style={{
                      border: "1px solid #d8dcff",
                      background: "#fff",
                      color: "var(--color-brand)",
                      borderRadius: 14,
                      padding: "9px 12px",
                      fontSize: 12,
                      fontWeight: 900,
                      cursor: "pointer",
                    }}
                  >
                    Preview
                  </button>

                  <button
                    type="button"
                    disabled={!primaryAssetUrl}
                    onClick={() => primaryAssetUrl ? window.open(primaryAssetUrl, "_blank", "noopener,noreferrer") : null}
                    style={{
                      border: "1px solid #e5eaf2",
                      background: primaryAssetUrl ? "#fff" : "#f8fafc",
                      color: primaryAssetUrl ? "var(--color-dark)" : "#94a3b8",
                      borderRadius: 14,
                      padding: "9px 12px",
                      fontSize: 12,
                      fontWeight: 900,
                      cursor: primaryAssetUrl ? "pointer" : "not-allowed",
                    }}
                  >
                    Open asset
                  </button>

                  <button
                    type="button"
                    onClick={() => navigator.clipboard?.writeText(liveDeliverable?.summary || "Client deliverable summary copied.")}
                    style={{
                      border: "1px solid #e5eaf2",
                      background: "#fff",
                      color: "var(--color-dark)",
                      borderRadius: 14,
                      padding: "9px 12px",
                      fontSize: 12,
                      fontWeight: 900,
                      cursor: "pointer",
                    }}
                  >
                    Copy summary
                  </button>

                  <button
                    type="button"
                    onClick={async () => {
                      const saved = await recordClientReviewAction("approved");
                      if (!saved) return;
                      setReviewStatus("approved");
                      setToastMessage("Deliverable approved.");
                    }}
                    style={{
                      border: "none",
                      background: "var(--color-teal)",
                      color: "#fff",
                      borderRadius: 14,
                      padding: "10px 14px",
                      fontSize: 12,
                      fontWeight: 950,
                      cursor: "pointer",
                    }}
                  >
                    👍 Approve
                  </button>

                  <button
                    type="button"
                    onClick={() => setShowRejectModal(true)}
                    style={{
                      border: "1px solid #fecaca",
                      background: "#fff",
                      color: "var(--color-red)",
                      borderRadius: 14,
                      padding: "10px 14px",
                      fontSize: 12,
                      fontWeight: 950,
                      cursor: "pointer",
                    }}
                  >
                    👎 Request changes
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

'''

src = src[:start] + new_section + src[end:]

PAGE.write_text(src, encoding="utf-8")

print("ACTIVITY_AND_OUTPUT_VIEWER_POLISHED")
print(f"Backup: {backup}")
print("Activity section:", src.count("Latest governed activity"))
print("Output viewer:", src.count("Execution output viewer"))
print("Enterprise modal preserved:", "showEnterpriseCatalogueModal" in src)
print("Right execution column locked:", src.count("Live execution flow") == 1 and src.count("Business profile applied") == 1 and src.count("Governed execution, every time.") == 1)
print("Old mutations:", src.count("applyHorizontalExecutionLayout") + src.count("applyPremiumExecutionSectionLayout"))