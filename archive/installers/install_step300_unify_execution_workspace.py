from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step300_unify_execution_workspace_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

old = '''              {executionState === "running" ? (
                <div>
                  <div style={{ fontSize: 28, marginBottom: 10 }}>⏳</div>
                  <div>Generating premium deliverables...</div>
                  <div
                    style={{
                      marginTop: 14,
                      height: 8,
                      width: 240,
                      borderRadius: 999,
                      background: "#dbeafe",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        width: "72%",
                        height: "100%",
                        borderRadius: 999,
                        background: "linear-gradient(135deg,#2563eb,#06b6d4)",
                      }}
                    />
                  </div>
                </div>
              ) : executionState === "completed" ? (
                <div>
                  <div style={{ fontSize: 28, marginBottom: 10 }}>✅</div>
                  <div>Deliverable ready for review</div>
                  <div style={{ marginTop: 6, color: "#64748b", fontSize: 12 }}>
                    Approval or feedback required
                  </div>
                </div>
              ) : (
                "Run an agent to generate deliverables"
              )}'''

new = '''              {executionState === "running" ? (
                <div>
                  <div style={{ fontSize: 28, marginBottom: 10 }}>⏳</div>
                  <div>Generating premium deliverables...</div>
                  <div
                    style={{
                      marginTop: 14,
                      height: 8,
                      width: 240,
                      borderRadius: 999,
                      background: "#dbeafe",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        width: "72%",
                        height: "100%",
                        borderRadius: 999,
                        background: "linear-gradient(135deg,#2563eb,#06b6d4)",
                      }}
                    />
                  </div>
                </div>
              ) : executionState === "completed" && liveDeliverable ? (
                <div style={{ width: "100%", textAlign: "left" }}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      gap: 12,
                      marginBottom: 12,
                    }}
                  >
                    <div
                      style={{
                        color: "#16a34a",
                        fontWeight: 900,
                        fontSize: 13,
                      }}
                    >
                      ✅ Latest deliverable ready
                    </div>

                    <div
                      style={{
                        color: "#64748b",
                        fontSize: 12,
                        fontWeight: 700,
                      }}
                    >
                      {liveDeliverable?.created_at || "Ready now"}
                    </div>
                  </div>

                  <div
                    style={{
                      color: "#0f172a",
                      fontSize: 18,
                      fontWeight: 900,
                      lineHeight: 1.25,
                      marginBottom: 8,
                    }}
                  >
                    {liveDeliverable?.title || "Premium ecommerce deliverable"}
                  </div>

                  <div
                    style={{
                      color: "#64748b",
                      fontSize: 13,
                      lineHeight: 1.55,
                      maxWidth: 420,
                    }}
                  >
                    {(liveDeliverable?.summary || "Client-ready deliverable generated.")
                      .slice(0, 150)}
                    {(liveDeliverable?.summary || "").length > 150 ? "..." : ""}
                  </div>

                  <div
                    style={{
                      marginTop: 14,
                      display: "flex",
                      gap: 8,
                      flexWrap: "wrap",
                    }}
                  >
                    {(liveDeliverable?.tags || ["Approval required"]).slice(0, 3).map((tag: string) => (
                      <span
                        key={tag}
                        style={{
                          border: "1px solid #dbeafe",
                          background: "#eff6ff",
                          color: "#2563eb",
                          borderRadius: 999,
                          padding: "7px 10px",
                          fontSize: 12,
                          fontWeight: 800,
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              ) : executionState === "completed" ? (
                <div>
                  <div style={{ fontSize: 28, marginBottom: 10 }}>✅</div>
                  <div>Deliverable ready for review</div>
                  <div style={{ marginTop: 6, color: "#64748b", fontSize: 12 }}>
                    Approval or feedback required
                  </div>
                </div>
              ) : (
                "Run an agent to generate deliverables"
              )}'''

if old not in text:
    raise SystemExit("ERROR: Execution workspace state block not found.")

text = text.replace(old, new)

PAGE.write_text(text, encoding="utf-8")

print("STEP_300_UNIFY_EXECUTION_WORKSPACE_INSTALLED")
print(f"Backup: {backup}")
print("STEP_300_OK")