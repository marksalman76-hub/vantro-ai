from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "app" / "admin" / "live-execution" / "page.tsx"

BACKUP = ROOT / "backups" / f"clickable_media_preview_cards_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "page.tsx")

s = TARGET.read_text(encoding="utf-8")

# Add selected preview state after normalized result if missing.
if "const [selectedPreviewCard, setSelectedPreviewCard]" not in s:
    s = s.replace(
        "const normalizedResult = normalizeExecutionPacket(result);",
        "const normalizedResult = normalizeExecutionPacket(result);\n  const [selectedPreviewCard, setSelectedPreviewCard] = useState<any>(null);"
    )

# Make cards clickable.
s = s.replace(
'''<div key={`${card.title}-${idx}`} style={{ border: "1px solid rgba(125,211,252,.28)", background: "rgba(14,165,233,.08)", borderRadius: 18, padding: 14 }}>''',
'''<button key={`${card.title}-${idx}`} onClick={() => setSelectedPreviewCard(card)} style={{ cursor: "pointer", textAlign: "left", border: "1px solid rgba(125,211,252,.28)", background: "rgba(14,165,233,.08)", borderRadius: 18, padding: 14 }}>'''
)

s = s.replace(
'''</div>
                    ))}
                  </div>
                ) : (''',
'''</button>
                    ))}
                  </div>
                ) : (''',
1
)

# Add selected preview panel before output pre block.
needle = '''<pre style={{ whiteSpace: "pre-wrap", maxHeight: 430, overflow: "auto", background: "#020617", border: "1px solid rgba(148,163,184,.2)", borderRadius: 22, padding: 20, color: "#e2e8f0", lineHeight: 1.6, fontSize: 14 }}>'''

panel = '''{selectedPreviewCard ? (
                <div style={{ marginBottom: 14, border: "1px solid rgba(34,211,238,.35)", background: "rgba(8,47,73,.45)", borderRadius: 22, padding: 18 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", marginBottom: 8 }}>
                    <div style={{ color: "#67e8f9", fontWeight: 950 }}>{selectedPreviewCard.title}</div>
                    <button onClick={() => setSelectedPreviewCard(null)} style={{ border: "1px solid rgba(148,163,184,.35)", background: "rgba(15,23,42,.8)", color: "#fff", borderRadius: 999, padding: "7px 10px", cursor: "pointer" }}>Close</button>
                  </div>
                  <div style={{ color: "#dbeafe", lineHeight: 1.5 }}>{selectedPreviewCard.detail}</div>
                  <div style={{ marginTop: 12, color: "#cbd5e1", fontSize: 13 }}>
                    Full matching deliverable details are available in the live output panel below.
                  </div>
                </div>
              ) : null}

              '''

if panel.strip() not in s and needle in s:
    s = s.replace(needle, panel + needle)

TARGET.write_text(s, encoding="utf-8")

print("MEDIA_PREVIEW_CARDS_CLICKABLE")
print("Backup:", BACKUP)