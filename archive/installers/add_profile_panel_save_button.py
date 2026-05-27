from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_profile_save_button_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

old = '''                    <div style={{ marginTop: 8, color: "var(--color-muted)", fontSize: 12 }}>
                      {clientEmail || "No email shown"}
                    </div>
                  </div>

                  <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
'''

new = '''                    <div style={{ marginTop: 8, color: "var(--color-muted)", fontSize: 12 }}>
                      {clientEmail || "No email shown"}
                    </div>

                    <button
                      type="button"
                      onClick={saveBusinessProfile}
                      style={{
                        marginTop: 12,
                        border: 0,
                        borderRadius: 12,
                        padding: "10px 12px",
                        background: "linear-gradient(135deg,#4f46e5,#4338ca)",
                        color: "#fff",
                        fontSize: 12.4,
                        fontWeight: 900,
                        cursor: "pointer",
                      }}
                    >
                      Save profile
                    </button>
                  </div>

                  <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
'''

if old not in text:
    raise SystemExit("Could not find profile email block safely.")

text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")

print("PROFILE_PANEL_SAVE_BUTTON_ADDED")
print(f"Backup: {backup}")