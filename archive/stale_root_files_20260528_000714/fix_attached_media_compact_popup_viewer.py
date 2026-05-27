from pathlib import Path
from datetime import datetime

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_attached_media_compact_popup_{timestamp}.tsx"

s = target.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

replacements = {
    'fontSize: 20': 'fontSize: 16',
    'lineHeight: 1.6': 'lineHeight: 1.45',
    'marginBottom: 16': 'marginBottom: 10',
    'padding: "8px 11px"': 'padding: "6px 9px"',
    'fontSize: 11.8': 'fontSize: 11',
    'gridTemplateColumns: "repeat(auto-fit,minmax(120px,1fr))"': 'gridTemplateColumns: "repeat(auto-fit,minmax(92px,1fr))"',
    'borderRadius: 16,\n                              padding: 10,': 'borderRadius: 14,\n                              padding: 8,',
    'Preview\n                  </button>': 'Preview in popup\n                  </button>',
    'No downloadable asset is attached yet.': 'No asset generated yet.',
}

for old, new in replacements.items():
    s = s.replace(old, new)

# Add a clear compact real-assets note near the Attached media heading if not already present.
old_heading = '''<div style={{ color: "var(--color-muted)", fontSize: 11, fontWeight: 700, marginBottom: 8 }}>
                      Attached media
                    </div>'''

new_heading = '''<div style={{ color: "var(--color-muted)", fontSize: 11, fontWeight: 700, marginBottom: 6 }}>
                      Attached media
                    </div>
                    <div style={{ color: "#94a3b8", fontSize: 10.5, fontWeight: 650, marginBottom: 8 }}>
                      Real generated/uploaded assets only. Use popup preview to inspect media.
                    </div>'''

if old_heading in s and "Use popup preview to inspect media" not in s:
    s = s.replace(old_heading, new_heading)

# Ensure empty/no-asset copy is customer-safe if present.
s = s.replace("No downloadable asset is attached yet.", "No asset generated yet.")

target.write_text(s, encoding="utf-8")

print("ATTACHED_MEDIA_COMPACT_POPUP_VIEWER_FIXED")
print(f"Backup: {backup}")
print("Updated:", target)