from pathlib import Path
from datetime import datetime
import re

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_dedicated_media_popup_{timestamp}.tsx"

s = target.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

if "showMediaPreviewOverlay" not in s:
    marker = 'const [showDeliverableModal, setShowDeliverableModal] = useState(false);'
    if marker not in s:
        raise SystemExit("showDeliverableModal state marker not found.")
    s = s.replace(
        marker,
        marker + '\n  const [showMediaPreviewOverlay, setShowMediaPreviewOverlay] = useState(false);'
    )

s = s.replace(
    'onClick={() => setShowDeliverableModal(true)}\n                    style={{\n                      border: "1px solid rgba(37, 99, 235, 0.14)",',
    'onClick={() => setShowMediaPreviewOverlay(true)}\n                    style={{\n                      border: "1px solid rgba(37, 99, 235, 0.14)",',
    1
)

overlay_marker = "DEDICATED_MEDIA_PREVIEW_OVERLAY_V1"

overlay = r'''
      {/* DEDICATED_MEDIA_PREVIEW_OVERLAY_V1 */}
      {showMediaPreviewOverlay ? (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Media preview popup"
          onClick={() => setShowMediaPreviewOverlay(false)}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 2147483647,
            background: "rgba(15, 23, 42, 0.76)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 24,
          }}
        >
          <div
            onClick={(event) => event.stopPropagation()}
            style={{
              width: "min(860px, 94vw)",
              maxHeight: "84vh",
              overflow: "hidden",
              borderRadius: 26,
              background: "#ffffff",
              border: "1px solid #e5eaf2",
              boxShadow: "0 30px 90px rgba(15, 23, 42, 0.35)",
            }}
          >
            <div
              style={{
                padding: "18px 20px",
                borderBottom: "1px solid #e5eaf2",
                display: "flex",
                justifyContent: "space-between",
                gap: 16,
                alignItems: "flex-start",
              }}
            >
              <div>
                <div
                  style={{
                    color: "var(--color-brand)",
                    fontSize: 11,
                    fontWeight: 900,
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
                  Real generated/uploaded assets only.
                </p>
              </div>

              <button
                type="button"
                onClick={() => setShowMediaPreviewOverlay(false)}
                style={{
                  border: "1px solid #e5eaf2",
                  background: "#ffffff",
                  color: "#334155",
                  borderRadius: 999,
                  padding: "8px 12px",
                  fontWeight: 850,
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
                background: "#f8fafc",
                maxHeight: "calc(84vh - 92px)",
                overflow: "auto",
              }}
            >
              {primaryAssetUrl ? (
                <div
                  style={{
                    borderRadius: 22,
                    background: "#ffffff",
                    border: "1px solid #e5eaf2",
                    minHeight: 320,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    overflow: "hidden",
                  }}
                >
                  <img
                    src={primaryAssetUrl}
                    alt={selectedAsset?.title || selectedAsset?.name || "Generated media asset"}
                    style={{
                      maxWidth: "100%",
                      maxHeight: "62vh",
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
                    <div style={{ fontSize: 36, marginBottom: 10 }}>🖼️</div>
                    <h4 style={{ margin: 0, fontSize: 17, color: "#0f172a" }}>No asset generated yet</h4>
                    <p style={{ margin: "8px auto 0", maxWidth: 430, color: "#64748b", fontSize: 13, lineHeight: 1.55 }}>
                      Real generated media, uploaded brand files, previews, and deliverable assets will appear here once attached to the runtime result.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : null}
'''

if overlay_marker not in s:
    insert_pos = s.rfind("</main>")
    if insert_pos == -1:
        raise SystemExit("Could not find </main> insertion point.")
    s = s[:insert_pos] + overlay + "\n" + s[insert_pos:]

target.write_text(s, encoding="utf-8")

print("DEDICATED_MEDIA_POPUP_STATE_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {target}")