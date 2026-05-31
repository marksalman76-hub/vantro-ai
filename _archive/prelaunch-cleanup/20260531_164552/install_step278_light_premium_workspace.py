from pathlib import Path
from datetime import datetime

page = Path("frontend/src/app/client/page.tsx")

content = page.read_text(encoding="utf-8")

content = content.replace(
    'background: "radial-gradient(circle at top left,#071226 0%,#020617 60%,#01030a 100%)"',
    'background: "#f5f7fb"'
)

content = content.replace(
    'color: "#f8fafc"',
    'color: "#0f172a"'
)

content = content.replace(
    'const cardStyle = {',
    '''const cardStyle = {
  background: "#ffffff",
  border: "1px solid rgba(15,23,42,.06)",
  boxShadow: "0 10px 30px rgba(15,23,42,.05)",
'''
)

content = content.replace(
    'background: "rgba(15,23,42,.72)"',
    'background: "#ffffff"'
)

content = content.replace(
    'border: "1px solid rgba(148,163,184,.14)"',
    'border: "1px solid rgba(15,23,42,.06)"'
)

content = content.replace(
    'color: "#cbd5e1"',
    'color: "#475569"'
)

content = content.replace(
    'color: "#94a3b8"',
    'color: "#64748b"'
)

content = content.replace(
    'background: "rgba(2,6,23,.45)"',
    'background: "#ffffff"'
)

content = content.replace(
    'background: "rgba(255,255,255,.03)"',
    'background: "#ffffff"'
)

content = content.replace(
    'boxShadow: "0 0 0 1px rgba(255,255,255,.04)"',
    'boxShadow: "0 10px 30px rgba(15,23,42,.05)"'
)

content = content.replace(
    'background: "linear-gradient(135deg,#0f172a 0%,#111827 100%)"',
    'background: "#ffffff"'
)

content = content.replace(
    'background: "rgba(59,130,246,.12)"',
    'background: "rgba(59,130,246,.08)"'
)

content = content.replace(
    'background: "rgba(15,23,42,.92)"',
    'background: "#ffffff"'
)

content = content.replace(
    'border: "1px dashed rgba(148,163,184,.18)"',
    'border: "1px dashed rgba(148,163,184,.28)"'
)

backup = Path(
    f"backups/client_page_before_step278_apply_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
)

backup.write_text(page.read_text(encoding="utf-8"), encoding="utf-8")

page.write_text(content, encoding="utf-8")

print("STEP_278_LIGHT_PREMIUM_WORKSPACE_INSTALLED")
print("Backup:", backup)
print("STEP_278_OK")