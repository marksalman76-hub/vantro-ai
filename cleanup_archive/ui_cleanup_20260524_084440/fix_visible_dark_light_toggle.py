from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_visible_dark_light_toggle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

old_state = '  const [activeAccountPanel, setActiveAccountPanel] = useState("");'
new_state = '''  const [activeAccountPanel, setActiveAccountPanel] = useState("");
  const [darkModeEnabled, setDarkModeEnabled] = useState(false);'''

if old_state not in text:
    raise SystemExit("Could not find activeAccountPanel state.")

text = text.replace(old_state, new_state, 1)

old_main_style = '''        minHeight: "100vh",
        background: "#f4f7fb",
        color: "var(--color-dark)",'''

new_main_style = '''        minHeight: "100vh",
        background: darkModeEnabled ? "#0f172a" : "#f4f7fb",
        color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)",'''

if old_main_style not in text:
    raise SystemExit("Could not find main style block.")

text = text.replace(old_main_style, new_main_style, 1)

old_toggle = '''                <button
                  onClick={() => document.documentElement.classList.toggle("dark")}
                  style={{ width: "100%", border: "none", borderTop: "1px solid #edf1f6", background: "transparent", padding: "12px 8px", textAlign: "left", fontWeight: 800, cursor: "pointer", color: "var(--color-dark)" }}
                >
                  🌙 Toggle dark / light mode
                </button>'''

new_toggle = '''                <button
                  onClick={() => {
                    setDarkModeEnabled((previous) => !previous);
                    setToastMessage(darkModeEnabled ? "Light mode enabled." : "Dark mode enabled.");
                  }}
                  style={{ width: "100%", border: "none", borderTop: "1px solid #edf1f6", background: "transparent", padding: "12px 8px", textAlign: "left", fontWeight: 800, cursor: "pointer", color: "var(--color-dark)" }}
                >
                  {darkModeEnabled ? "☀️ Switch to light mode" : "🌙 Toggle dark / light mode"}
                </button>'''

if old_toggle not in text:
    raise SystemExit("Could not find dark/light toggle button.")

text = text.replace(old_toggle, new_toggle, 1)

path.write_text(text, encoding="utf-8")

print("VISIBLE_DARK_LIGHT_TOGGLE_FIXED")
print(f"Backup: {backup}")