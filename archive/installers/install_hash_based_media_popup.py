from pathlib import Path
from datetime import datetime
import re

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_hash_media_popup_{timestamp}.tsx"

s = target.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

# Replace Preview button opening with real hash link.
button_pattern = re.compile(
    r'''<button\s+onClick=\{\(\)\s*=>\s*setShowMediaPreviewOverlay\(true\)\}\s+style=\{\{(?P<style>[\s\S]*?)\}\}\s*>\s*Preview in popup\s*</button>''',
    re.MULTILINE,
)

match = button_pattern.search(s)
if not match:
    raise SystemExit("Preview button pattern not found.")

replacement = '''<a
                    href="#media-preview-popup"
                    style={{
''' + match.group("style") + '''
                      textDecoration: "none",
                      display: "inline-flex",
                      alignItems: "center",
                    }}
                  >
                    Preview in popup
                  </a>'''

s = s[:match.start()] + replacement + s[match.end():]

popup_marker = "HASH_MEDIA_PREVIEW_POPUP_V1"

popup = r'''
      {/* HASH_MEDIA_PREVIEW_POPUP_V1 */}
      <style>{`
        #media-preview-popup {
          display: none;
        }
        #media-preview-popup:target {
          display: flex;
        }
      `}</style>

      <div
        id="media-preview-popup"
        role="dialog"
        aria-modal="true"
        aria-label="Media preview popup"
        style={{
          position: "fixed",
          inset: 0,
          zIndex: 2147483647,
          alignItems: "center",
          justifyContent: "center",
          padding: 24,
          background: "rgba(15, 23, 42, 0.76)",
        }}
      >
        <a
          href="#"
          aria-label="Close media preview"
          style={{
            position: "absolute",
            inset: 0,
            display: "block",
            cursor: "default",
          }}
        />

        <div
          style={{
            position: "relative",
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

            <a
              href="#"
              style={{
                border: "1px solid #e5eaf2",
                background: "#ffffff",
                color: "#334155",
                borderRadius: 999,
                padding: "8px 12px",
                fontWeight: 850,
                fontSize: 12,
                cursor: "pointer",
                textDecoration: "none",
              }}
            >
              Close
            </a>
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
'''

if popup_marker not in s:
    insert_pos = s.rfind("</main>")
    if insert_pos == -1:
        raise SystemExit("Could not find </main> insertion point.")
    s = s[:insert_pos] + popup + "\n" + s[insert_pos:]

target.write_text(s, encoding="utf-8")

print("HASH_BASED_MEDIA_POPUP_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {target}")