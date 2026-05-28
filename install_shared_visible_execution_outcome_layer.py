from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"

backup = ROOT / "backups" / f"shared_visible_execution_outcome_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(admin_page, backup / "admin_page.tsx")
shutil.copy2(client_page, backup / "client_page.tsx")

# -------------------------
# ADMIN: add visible outcome controls
# -------------------------
s = admin_page.read_text(encoding="utf-8")

s = s.replace(
'''                              <div className="executionMetaRow">
                                <span>Provider: {item?.provider || "openai"}</span>
                                <span>Live: {item?.live_external_call_executed ? "Yes" : "No"}</span>
                                <span>Latency: {item?.latency_ms ? `${item.latency_ms}ms` : "—"}</span>
                              </div>
                              <div className="executionTimeline">
                                <span>Received</span>
                                <span>Governed</span>
                                <span>{item?.success ? "Completed" : "Review"}</span>
                              </div>''',
'''                              <div className="executionMetaRow">
                                <span>Provider: {item?.provider || "openai"}</span>
                                <span>Live: {item?.live_external_call_executed ? "Yes" : "No"}</span>
                                <span>Latency: {item?.latency_ms ? `${item.latency_ms}ms` : "—"}</span>
                              </div>

                              <div className="visibleOutcomeActions">
                                <button onClick={() => showToast("Outcome approved by admin.")}>Approve</button>
                                <button onClick={() => showToast("Amendment requested. Add revision notes in the task box and rerun.")}>Request amendment</button>
                                <button onClick={() => showToast("Outcome rejected by admin.")}>Reject</button>
                                <button onClick={() => navigator.clipboard.writeText(cleanMessage || "")}>Copy outcome</button>
                              </div>

                              <div className="executionTimeline">
                                <span>Generated</span>
                                <span>Review ready</span>
                                <span>{item?.success ? "Awaiting approval" : "Needs amendment"}</span>
                              </div>'''
)

if ".visibleOutcomeActions" not in s:
    s = s.replace(
'''        .executionTimeline span {''',
'''        .visibleOutcomeActions {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          margin-top: 14px;
        }
        .visibleOutcomeActions button {
          border: 1px solid rgba(148, 163, 184, .24);
          background: rgba(15, 23, 42, .88);
          color: #dbeafe;
          padding: 9px 12px;
          border-radius: 999px;
          font-weight: 850;
          cursor: pointer;
        }
        .visibleOutcomeActions button:first-child {
          background: rgba(20, 184, 166, .16);
          color: #5eead4;
          border-color: rgba(20, 184, 166, .35);
        }
        .visibleOutcomeActions button:nth-child(3) {
          background: rgba(239, 68, 68, .13);
          color: #fecaca;
          border-color: rgba(239, 68, 68, .32);
        }
        .executionTimeline span {'''
    )

admin_page.write_text(s, encoding="utf-8")

# -------------------------
# CLIENT: make output visibly render and add client actions
# -------------------------
c = client_page.read_text(encoding="utf-8")

# Insert derived client outcome variables after primaryAssetUrl if possible.
anchor = "const primaryAssetUrl"
idx = c.find(anchor)
if idx != -1 and "visibleClientOutcomeText" not in c:
    line_end = c.find("\n", idx)
    insert = '''
  const visibleClientOutcomeText =
    liveDeliverable?.output ||
    liveDeliverable?.generated_output ||
    liveDeliverable?.provider_output ||
    liveDeliverable?.content ||
    liveDeliverable?.summary ||
    liveDeliverable?.message ||
    "";
'''
    c = c[:line_end + 1] + insert + c[line_end + 1:]

# Replace obvious placeholder text in client viewer.
c = c.replace(
    "No asset generated yet",
    "No media asset generated yet"
)

c = c.replace(
    "Generated assets, uploaded brand files, previews, and deliverable media will appear here automatically.",
    "Generated images, files, previews, and deliverable media will appear here when included in the execution."
)

# Add visible output block before the media card closing area by targeting secure workspace footer.
old_footer = '''                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        gap: 12,
                        marginTop: 18,
                        fontSize: 11,
                        color: darkModeEnabled ? "#94a3b8" : "#94a3b8",
                      }}
                    >
                      <div>Secure asset workspace</div>
                      <div>Enterprise media pipeline</div>
                    </div>'''

new_footer = '''                    <div
                      style={{
                        marginTop: 14,
                        borderRadius: 16,
                        border: darkModeEnabled ? "1px solid rgba(99,102,241,.28)" : "1px solid #dbe4ee",
                        background: darkModeEnabled ? "rgba(2,6,23,.72)" : "#ffffff",
                        padding: 14,
                      }}
                    >
                      <div style={{ fontSize: 11, fontWeight: 900, color: darkModeEnabled ? "#93c5fd" : "var(--color-brand)", textTransform: "uppercase", letterSpacing: ".08em", marginBottom: 8 }}>
                        Generated outcome
                      </div>
                      <pre style={{ whiteSpace: "pre-wrap", margin: 0, maxHeight: 260, overflow: "auto", fontFamily: "inherit", fontSize: 13, lineHeight: 1.55, color: darkModeEnabled ? "#e5e7eb" : "var(--color-dark)" }}>
                        {visibleClientOutcomeText || "No generated outcome is ready yet. Run an agent to create a client deliverable."}
                      </pre>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 12 }}>
                        <button onClick={() => setReviewStatus("approved")} style={{ border: 0, borderRadius: 999, padding: "9px 12px", background: "#dcfce7", color: "var(--color-teal)", fontWeight: 900 }}>Approve</button>
                        <button onClick={() => setReviewStatus("rejected")} style={{ border: 0, borderRadius: 999, padding: "9px 12px", background: "#fee2e2", color: "var(--color-red)", fontWeight: 900 }}>Reject</button>
                        <button onClick={() => setReviewStatus("rejected")} style={{ border: darkModeEnabled ? "1px solid rgba(148,163,184,.28)" : "1px solid #dbe4ee", borderRadius: 999, padding: "9px 12px", background: darkModeEnabled ? "rgba(15,23,42,.88)" : "#fff", color: darkModeEnabled ? "#bfdbfe" : "var(--color-brand)", fontWeight: 900 }}>Request amendment</button>
                        <button onClick={() => navigator.clipboard?.writeText(visibleClientOutcomeText || "")} style={{ border: darkModeEnabled ? "1px solid rgba(148,163,184,.28)" : "1px solid #dbe4ee", borderRadius: 999, padding: "9px 12px", background: darkModeEnabled ? "rgba(15,23,42,.88)" : "#fff", color: darkModeEnabled ? "#bfdbfe" : "var(--color-brand)", fontWeight: 900 }}>Copy</button>
                      </div>
                    </div>

                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        gap: 12,
                        marginTop: 18,
                        fontSize: 11,
                        color: darkModeEnabled ? "#94a3b8" : "#94a3b8",
                      }}
                    >
                      <div>Secure asset workspace</div>
                      <div>Enterprise media pipeline</div>
                    </div>'''

if old_footer in c and "Generated outcome" not in c:
    c = c.replace(old_footer, new_footer)
else:
    print("CLIENT_FOOTER_TARGET_NOT_FOUND_OR_ALREADY_PATCHED")

client_page.write_text(c, encoding="utf-8")

print("SHARED_VISIBLE_EXECUTION_OUTCOME_LAYER_INSTALLED")
print(f"Backup folder: {backup}")
print(f"Updated: {admin_page}")
print(f"Updated: {client_page}")