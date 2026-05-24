from pathlib import Path
from datetime import datetime
import re

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_guaranteed_deliverable_popup_{timestamp}.tsx"

s = target.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

# Add guaranteed popup open/close helpers before return.
if "openGuaranteedDeliverablePopup" not in s:
    return_pos = s.find("return (")
    if return_pos == -1:
        raise SystemExit("Could not find return block.")

    helpers = r'''
  const openGuaranteedDeliverablePopup = () => {
    setShowDeliverableModal(true);
    window.requestAnimationFrame(() => {
      const popup = document.getElementById("guaranteed-deliverable-media-popup");
      if (popup) popup.style.display = "flex";
    });
  };

  const closeGuaranteedDeliverablePopup = () => {
    setShowDeliverableModal(false);
    const popup = document.getElementById("guaranteed-deliverable-media-popup");
    if (popup) popup.style.display = "none";
  };

'''
    s = s[:return_pos] + helpers + s[return_pos:]

# Force the visible preview button to use guaranteed popup.
s = s.replace('onClick={() => setShowDeliverableModal(true)}', 'onClick={openGuaranteedDeliverablePopup}')
s = s.replace("Preview in popup", "Preview in popup")

marker = "GUARANTEED_DELIVERABLE_MEDIA_POPUP_V1"

popup = r'''
      {/* GUARANTEED_DELIVERABLE_MEDIA_POPUP_V1 */}
      <div
        id="guaranteed-deliverable-media-popup"
        role="dialog"
        aria-modal="true"
        aria-label="Deliverable media preview"
        onClick={closeGuaranteedDeliverablePopup}
        style={{
          position: "fixed",
          inset: 0,
          zIndex: 99999,
          display: "none",
          alignItems: "center",
          justifyContent: "center",
          padding: 24,
          background: "rgba(15, 23, 42, 0.76)",
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
              onClick={closeGuaranteedDeliverablePopup}
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
          </div>
        </div>
      </div>
'''

if marker not in s:
    insert_pos = s.rfind("</main>")
    if insert_pos == -1:
        raise SystemExit("Could not find </main> insertion point.")
    s = s[:insert_pos] + popup + "\n" + s[insert_pos:]

target.write_text(s, encoding="utf-8")

print("GUARANTEED_DELIVERABLE_POPUP_FIXED")
print(f"Backup: {backup}")
print("Updated:", target)