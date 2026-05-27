from pathlib import Path
from datetime import datetime
import re

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_output_viewer_modal_compact_{timestamp}.tsx"

s = target.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

# 1) Ensure popup state exists.
if "showDeliverableModal" not in s:
    first_state = re.search(r"(\n\s*const\s+\[[^\]]+,\s*set[^\]]+\]\s*=\s*useState\([^\n]*\);)", s)
    if not first_state:
        raise SystemExit("Could not find useState insertion point.")
    s = s[:first_state.end()] + "\n  const [showDeliverableModal, setShowDeliverableModal] = useState(false);" + s[first_state.end():]

# 2) Force Preview button to open popup.
s = re.sub(
    r'onClick=\{\(\)\s*=>\s*setShowDeliverableModal\(true\)\}',
    'onClick={() => setShowDeliverableModal(true)}',
    s,
)

# 3) Compact the media preview panel text/card.
s = s.replace("No live asset attached", "No asset generated yet")
s = s.replace("Media preview unavailable", "Media preview")
s = s.replace("Waiting for uploaded or generated assets", "Waiting for real generated or uploaded assets")

# Reduce obvious oversized preview heights if present.
s = s.replace('minHeight: 260', 'minHeight: 148')
s = s.replace('minHeight: 240', 'minHeight: 148')
s = s.replace('minHeight: 220', 'minHeight: 148')
s = s.replace('height: 260', 'height: 148')
s = s.replace('height: 240', 'height: 148')
s = s.replace('height: 220', 'height: 148')
s = s.replace('padding: 28', 'padding: 16')
s = s.replace('padding: 24', 'padding: 16')

# 4) Add a guaranteed popup modal before the final main close.
modal_marker = "OUTPUT_VIEWER_POPUP_MODAL_LOCKED_V1"

modal = r'''
      {/* OUTPUT_VIEWER_POPUP_MODAL_LOCKED_V1 */}
      {showDeliverableModal ? (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Deliverable media preview"
          onClick={() => setShowDeliverableModal(false)}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 9999,
            background: "rgba(15, 23, 42, 0.72)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 24,
          }}
        >
          <div
            onClick={(event) => event.stopPropagation()}
            style={{
              width: "min(920px, 96vw)",
              maxHeight: "86vh",
              overflow: "hidden",
              borderRadius: 28,
              background: "#ffffff",
              border: "1px solid rgba(226, 232, 240, 0.92)",
              boxShadow: "0 30px 90px rgba(15, 23, 42, 0.32)",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                gap: 16,
                alignItems: "flex-start",
                padding: "18px 20px",
                borderBottom: "1px solid #e5eaf2",
              }}
            >
              <div>
                <div
                  style={{
                    color: "var(--color-brand)",
                    fontSize: 11,
                    fontWeight: 850,
                    letterSpacing: ".13em",
                    textTransform: "uppercase",
                  }}
                >
                  Media preview
                </div>
                <h3 style={{ margin: "6px 0 0", fontSize: 18, color: "#0f172a" }}>
                  {selectedAsset?.title || selectedAsset?.name || liveDeliverable?.title || "Client deliverable"}
                </h3>
                <p style={{ margin: "6px 0 0", color: "#64748b", fontSize: 12.5 }}>
                  Real generated/uploaded media and runtime deliverables only.
                </p>
              </div>

              <button
                type="button"
                onClick={() => setShowDeliverableModal(false)}
                style={{
                  border: "1px solid #e5eaf2",
                  background: "#fff",
                  color: "#334155",
                  borderRadius: 999,
                  padding: "8px 12px",
                  fontWeight: 800,
                  fontSize: 12,
                  cursor: "pointer",
                }}
              >
                Close
              </button>
            </div>

            <div
              style={{
                padding: 20,
                maxHeight: "calc(86vh - 96px)",
                overflow: "auto",
                background: "#f8fafc",
              }}
            >
              {selectedAsset?.url || selectedAsset?.image_url || selectedAsset?.src ? (
                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    minHeight: 320,
                    borderRadius: 22,
                    background: "#ffffff",
                    border: "1px solid #e5eaf2",
                    overflow: "hidden",
                  }}
                >
                  <img
                    src={selectedAsset?.url || selectedAsset?.image_url || selectedAsset?.src}
                    alt={selectedAsset?.title || selectedAsset?.name || "Generated media asset"}
                    style={{
                      maxWidth: "100%",
                      maxHeight: "64vh",
                      objectFit: "contain",
                      display: "block",
                    }}
                  />
                </div>
              ) : (
                <div
                  style={{
                    minHeight: 260,
                    borderRadius: 22,
                    background: "#ffffff",
                    border: "1px dashed #cbd5e1",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    textAlign: "center",
                    padding: 28,
                  }}
                >
                  <div>
                    <div style={{ fontSize: 34, marginBottom: 10 }}>🖼️</div>
                    <h4 style={{ margin: 0, fontSize: 16, color: "#0f172a" }}>No asset generated yet</h4>
                    <p style={{ margin: "8px auto 0", maxWidth: 420, color: "#64748b", fontSize: 13, lineHeight: 1.55 }}>
                      Real generated media, uploaded brand files, previews, and deliverable assets will appear here once attached to the runtime result.
                    </p>
                  </div>
                </div>
              )}

              <div style={{ marginTop: 16, display: "flex", gap: 10, flexWrap: "wrap" }}>
                <button
                  type="button"
                  disabled={!deliverableDownloadUrl}
                  onClick={() => {
                    if (!deliverableDownloadUrl) {
                      setToastMessage("No asset generated yet.");
                      return;
                    }
                    window.open(deliverableDownloadUrl, "_blank", "noopener,noreferrer");
                  }}
                  style={{
                    border: "1px solid #e5eaf2",
                    background: deliverableDownloadUrl ? "#ffffff" : "#f8fafc",
                    color: deliverableDownloadUrl ? "#334155" : "#94a3b8",
                    borderRadius: 999,
                    padding: "9px 13px",
                    fontWeight: 800,
                    fontSize: 12,
                    cursor: deliverableDownloadUrl ? "pointer" : "not-allowed",
                  }}
                >
                  Open asset
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : null}
'''

if modal_marker not in s:
    insert_pos = s.rfind("</main>")
    if insert_pos == -1:
      raise SystemExit("Could not find </main> insertion point.")
    s = s[:insert_pos] + modal + "\n" + s[insert_pos:]

target.write_text(s, encoding="utf-8")

print("OUTPUT_VIEWER_MODAL_AND_COMPACT_MEDIA_FIXED")
print(f"Backup: {backup}")
print("Updated:", target)