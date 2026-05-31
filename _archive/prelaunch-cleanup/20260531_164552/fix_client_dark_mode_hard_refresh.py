from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_dark_mode_hard_refresh_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

old = '''const [darkModeEnabled, setDarkModeEnabled] = useState(false);'''
new = '''const [darkModeEnabled, setDarkModeEnabled] = useState(() => {
    if (typeof window === "undefined") return false;
    return window.localStorage.getItem("client_workspace_dark_mode") === "dark";
  });'''

if old not in s:
    print("State line already changed or not found. Continuing safely.")
else:
    s = s.replace(old, new, 1)

old_effect = '''useEffect(() => {
    try {
      const savedTheme = window.localStorage.getItem("client_workspace_dark_mode");
      const shouldUseDarkMode = savedTheme === "dark";
      setDarkModeEnabled(shouldUseDarkMode);
      document.documentElement.dataset.clientTheme = shouldUseDarkMode ? "dark" : "light";
    } catch {}
  }, []);'''

new_effect = '''useEffect(() => {
    try {
      const savedTheme = window.localStorage.getItem("client_workspace_dark_mode");
      const shouldUseDarkMode = savedTheme === "dark";
      setDarkModeEnabled(shouldUseDarkMode);
      document.documentElement.dataset.clientTheme = shouldUseDarkMode ? "dark" : "light";
    } catch {}
  }, []);

  useEffect(() => {
    try {
      document.documentElement.dataset.clientTheme = darkModeEnabled ? "dark" : "light";
    } catch {}
  }, [darkModeEnabled]);'''

if old_effect in s:
    s = s.replace(old_effect, new_effect, 1)

TARGET.write_text(s, encoding="utf-8")

print("CLIENT_DARK_MODE_HARD_REFRESH_FINAL_FIXED")
print(f"Backup: {backup}")