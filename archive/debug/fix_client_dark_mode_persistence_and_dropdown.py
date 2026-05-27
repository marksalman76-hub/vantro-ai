from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_dark_mode_persistence_dropdown_{stamp}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

old = 'const [darkModeEnabled, setDarkModeEnabled] = useState(false);'
new = '''const [darkModeEnabled, setDarkModeEnabled] = useState(false);
  const setAndPersistDarkMode = (nextValue: boolean) => {
    setDarkModeEnabled(nextValue);
    try {
      window.localStorage.setItem("client_workspace_dark_mode", nextValue ? "dark" : "light");
      document.documentElement.dataset.clientTheme = nextValue ? "dark" : "light";
    } catch {}
  };'''
if old not in s:
    raise SystemExit("FAILED: darkMode state marker not found")
s = s.replace(old, new, 1)

old = '''const profileMenuRef = useRef<HTMLDetailsElement | null>(null);


  const shellStyle = {'''
new = '''const profileMenuRef = useRef<HTMLDetailsElement | null>(null);

  useEffect(() => {
    try {
      const savedTheme = window.localStorage.getItem("client_workspace_dark_mode");
      const shouldUseDarkMode = savedTheme === "dark";
      setDarkModeEnabled(shouldUseDarkMode);
      document.documentElement.dataset.clientTheme = shouldUseDarkMode ? "dark" : "light";
    } catch {}
  }, []);


  const shellStyle = {'''
if old not in s:
    raise SystemExit("FAILED: profileMenuRef insertion marker not found")
s = s.replace(old, new, 1)

old = '''<div
                style={{
                  position: "absolute",
                  right: 0,
                  top: 54,
                  width: 280,
                  background: "#fff",
                  border: "1px solid #e5eaf2",
                  borderRadius: 18,
                  boxShadow: "0 24px 60px rgba(15,23,42,.18)",
                  padding: 14,
                  zIndex: 50,
                }}
              >'''
new = '''<div
                style={{
                  position: "absolute",
                  right: 0,
                  top: 54,
                  width: 280,
                  background: darkModeEnabled ? "linear-gradient(180deg, rgba(10,22,46,.98), rgba(7,16,34,.99))" : "#fff",
                  border: darkModeEnabled ? "1px solid rgba(129,140,248,.28)" : "1px solid #e5eaf2",
                  borderRadius: 18,
                  boxShadow: darkModeEnabled ? "0 24px 70px rgba(0,0,0,.42)" : "0 24px 60px rgba(15,23,42,.18)",
                  padding: 14,
                  zIndex: 50,
                  color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)",
                }}
              >'''
if old not in s:
    raise SystemExit("FAILED: dropdown container marker not found")
s = s.replace(old, new, 1)

replacements = {
'''<div style={{ display: "flex", gap: 12, alignItems: "center", paddingBottom: 12, borderBottom: "1px solid #edf1f6" }}>''':
'''<div style={{ display: "flex", gap: 12, alignItems: "center", paddingBottom: 12, borderBottom: darkModeEnabled ? "1px solid rgba(129,140,248,.24)" : "1px solid #edf1f6" }}>''',

'''<div style={{ width: 46, height: 46, borderRadius: 999, background: "var(--color-dark)", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800 }}>{clientInitials}</div>''':
'''<div style={{ width: 46, height: 46, borderRadius: 999, background: darkModeEnabled ? "linear-gradient(135deg,#4f46e5,#7c3aed)" : "var(--color-dark)", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800 }}>{clientInitials}</div>''',

'''<div style={{ fontWeight: 800, color: "var(--color-dark)" }}>{clientDisplayName}</div>''':
'''<div style={{ fontWeight: 800, color: darkModeEnabled ? "#ffffff" : "var(--color-dark)" }}>{clientDisplayName}</div>''',

'''<div style={{ fontSize: 12, color: "var(--color-muted)" }}>{clientEmail || accountPackage}</div>''':
'''<div style={{ fontSize: 12, color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)" }}>{clientEmail || accountPackage}</div>''',

'''<div style={{ fontSize: 12, fontWeight: 700, marginTop: 4, color: "var(--color-muted)" }}>''':
'''<div style={{ fontSize: 12, fontWeight: 700, marginTop: 4, color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)" }}>''',

'''style={{ width: "100%", border: "none", background: "transparent", padding: "11px 8px", textAlign: "left", fontWeight: 700, cursor: "pointer", color: "var(--color-dark)" }}''':
'''style={{ width: "100%", border: "none", background: "transparent", padding: "11px 8px", textAlign: "left", fontWeight: 700, cursor: "pointer", color: darkModeEnabled ? "#e2e8f0" : "var(--color-dark)" }}''',

'''style={{ width: "100%", border: "none", borderTop: "1px solid #edf1f6", background: "transparent", padding: "12px 8px", textAlign: "left", fontWeight: 800, cursor: "pointer", color: "var(--color-dark)" }}''':
'''style={{ width: "100%", border: "none", borderTop: darkModeEnabled ? "1px solid rgba(129,140,248,.24)" : "1px solid #edf1f6", background: "transparent", padding: "12px 8px", textAlign: "left", fontWeight: 800, cursor: "pointer", color: darkModeEnabled ? "#e2e8f0" : "var(--color-dark)" }}'''
}

for old_text, new_text in replacements.items():
    if old_text not in s:
        print(f"WARNING: marker not found, skipped: {old_text[:90]}")
    s = s.replace(old_text, new_text)

old = '''onClick={() => {
                    setDarkModeEnabled((previous) => !previous);
                    setToastMessage(darkModeEnabled ? "Light mode enabled." : "Dark mode enabled.");
                  }}'''
new = '''onClick={() => {
                    const nextMode = !darkModeEnabled;
                    setAndPersistDarkMode(nextMode);
                    setToastMessage(nextMode ? "Dark mode enabled." : "Light mode enabled.");
                  }}'''
if old not in s:
    raise SystemExit("FAILED: profile dropdown dark toggle marker not found")
s = s.replace(old, new, 1)

old = '''onClick={() => document.documentElement.classList.toggle("dark")}'''
new = '''onClick={() => {
                        const nextMode = !darkModeEnabled;
                        setAndPersistDarkMode(nextMode);
                        setToastMessage(nextMode ? "Dark mode enabled." : "Light mode enabled.");
                      }}'''
if old not in s:
    raise SystemExit("FAILED: account settings dark toggle marker not found")
s = s.replace(old, new, 1)

TARGET.write_text(s, encoding="utf-8")

print("CLIENT_DARK_MODE_PERSISTENCE_AND_DROPDOWN_FIXED")
print(f"Backup: {backup}")