from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "app" / "admin" / "live-execution" / "page.tsx"

BACKUP = ROOT / "backups" / f"media_preview_modal_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "page.tsx")

s = TARGET.read_text(encoding="utf-8")

# Ensure selected preview state exists.
if "const [selectedPreviewCard, setSelectedPreviewCard]" not in s:
    s = s.replace(
        "const normalizedResult = normalizeExecutionPacket(result);",
        "const normalizedResult = normalizeExecutionPacket(result);\n  const [selectedPreviewCard, setSelectedPreviewCard] = useState<any>(null);"
    )

# Ensure media preview cards are buttons and preserve correct type.
s = s.replace(
    '<button key={`${card.title}-${idx}`} onClick={() => setSelectedPreviewCard(card)} style={{ cursor: "pointer", textAlign: "left", border:',
    '<button type="button" key={`${card.title}-${idx}`} onClick={() => setSelectedPreviewCard(card)} style={{ cursor: "pointer", textAlign: "left", border:'
)

# Remove old inline selectedPreviewCard panel if it exists.
s = re.sub(
    r'\{selectedPreviewCard \? \(\s*<div style=\{\{ marginBottom: 14, border: "1px solid rgba\(34,211,238,\.35\)".*?</div>\s*\) : null\}\s*',
    "",
    s,
    flags=re.S,
)

modal = r'''
      {selectedPreviewCard ? (
        <div
          onClick={() => setSelectedPreviewCard(null)}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 9999,
            background: "rgba(2,6,23,.78)",
            backdropFilter: "blur(14px)",
            display: "grid",
            placeItems: "center",
            padding: 24,
          }}
        >
          <div
            onClick={(event) => event.stopPropagation()}
            style={{
              width: "min(860px, 94vw)",
              maxHeight: "82vh",
              overflow: "auto",
              border: "1px solid rgba(34,211,238,.35)",
              background: "linear-gradient(135deg, rgba(15,23,42,.98), rgba(8,47,73,.96))",
              borderRadius: 28,
              padding: 28,
              boxShadow: "0 40px 120px rgba(0,0,0,.45)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", gap: 16, marginBottom: 18 }}>
              <div>
                <div style={{ color: "#67e8f9", fontWeight: 950, fontSize: 13, letterSpacing: ".08em", textTransform: "uppercase" }}>
                  Media Preview Detail
                </div>
                <h2 style={{ margin: "8px 0 0", color: "#fff", fontSize: 30 }}>
                  {selectedPreviewCard.title}
                </h2>
              </div>
              <button
                type="button"
                onClick={() => setSelectedPreviewCard(null)}
                style={{
                  border: "1px solid rgba(148,163,184,.35)",
                  background: "rgba(15,23,42,.9)",
                  color: "#fff",
                  borderRadius: 999,
                  padding: "10px 14px",
                  cursor: "pointer",
                  fontWeight: 900,
                }}
              >
                Close
              </button>
            </div>

            <div style={{ color: "#dbeafe", lineHeight: 1.55, fontSize: 17, marginBottom: 18 }}>
              {selectedPreviewCard.detail}
            </div>

            <div style={{
              border: "1px solid rgba(125,211,252,.22)",
              background: "rgba(2,6,23,.58)",
              borderRadius: 22,
              padding: 18,
              color: "#e2e8f0",
              whiteSpace: "pre-wrap",
              lineHeight: 1.6,
              fontSize: 14,
            }}>
              {outputText || "No output text available yet."}
            </div>
          </div>
        </div>
      ) : null}
'''

# Insert modal just before final main/page closing area. Use return JSX marker safely.
if "Media Preview Detail" not in s:
    # put after top-level main content but before closing fragment/main if possible
    marker = "\n    </main>"
    if marker in s:
        s = s.replace(marker, modal + marker, 1)
    else:
        s = s.replace("\n  );", modal + "\n  );", 1)

TARGET.write_text(s, encoding="utf-8")

print("MEDIA_PREVIEW_CLICK_MODAL_FIXED")
print("Backup:", BACKUP)