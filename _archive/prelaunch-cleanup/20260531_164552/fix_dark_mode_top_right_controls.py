from pathlib import Path
from datetime import datetime
import re

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_dark_top_right_controls_{timestamp}.tsx"

s = target.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

# Make ACTIVE pill readable in dark mode.
s = s.replace(
    'color: "#ffffff",\n                        fontWeight: 900,\n                      }}\n                    >\n                      ACTIVE',
    'color: darkModeEnabled ? "#22c55e" : "#059669",\n                        fontWeight: 950,\n                        textShadow: darkModeEnabled ? "0 0 18px rgba(34,197,94,.34)" : "none",\n                      }}\n                    >\n                      ACTIVE',
)

# Catch alternate ACTIVE text style if current structure differs.
s = re.sub(
    r'(>\s*ACTIVE\s*</)',
    r'>ACTIVE<',
    s,
    count=1,
)

# Strengthen ACTIVE pill background/border where present.
s = s.replace(
    'background: "#fff",\n                    color: "#10b981",',
    'background: darkModeEnabled ? "rgba(2, 18, 36, .92)" : "#fff",\n                    color: darkModeEnabled ? "#22c55e" : "#10b981",',
)

s = s.replace(
    'border: "1px solid #e5eaf2",\n                    background: "#fff",',
    'border: darkModeEnabled ? "1px solid rgba(34,197,94,.42)" : "1px solid #e5eaf2",\n                    background: darkModeEnabled ? "rgba(2, 18, 36, .92)" : "#fff",',
    1,
)

# Improve profile circle visibility in dark mode by strengthening button surfaces.
s = s.replace(
    'background: "#fff",\n                    color: "var(--color-dark)",',
    'background: darkModeEnabled ? "linear-gradient(135deg, #4f46e5, #7c3aed)" : "#fff",\n                    color: darkModeEnabled ? "#ffffff" : "var(--color-dark)",',
    1,
)

s = s.replace(
    'boxShadow: "0 16px 38px rgba(15,23,42,.12)",',
    'boxShadow: darkModeEnabled ? "0 0 0 4px rgba(99,102,241,.18), 0 18px 46px rgba(79,70,229,.36)" : "0 16px 38px rgba(15,23,42,.12)",',
    1,
)

# Keep notification/profile controls aligned and visible.
s = s.replace(
    'borderRadius: 999,\n                    padding: "10px 14px",',
    'borderRadius: 999,\n                    padding: "10px 16px",',
    1,
)

target.write_text(s, encoding="utf-8")

print("DARK_MODE_TOP_RIGHT_CONTROLS_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {target}")