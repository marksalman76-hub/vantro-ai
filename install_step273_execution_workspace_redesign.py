from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step273_execution_workspace_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

text = text.replace(
    'gridTemplateColumns: "1.05fr .95fr"',
    'gridTemplateColumns: "minmax(620px,1.15fr) minmax(420px,.85fr)"'
)

text = text.replace(
    'gap: 20,',
    'gap: 16,'
)

text = text.replace(
    'padding: 24,',
    'padding: 20,'
)

text = text.replace(
    'minHeight: 640,',
    'minHeight: 520,'
)

text = text.replace(
    'fontSize: 38,',
    'fontSize: 32,'
)

text = text.replace(
    'fontSize: 18,',
    'fontSize: 16,'
)

text = text.replace(
    'height: 320,',
    'height: 250,'
)

text = text.replace(
    'minHeight: 420,',
    'minHeight: 360,'
)

text = text.replace(
    'padding: "18px 20px"',
    'padding: "14px 16px"'
)

text = text.replace(
    'padding: "16px 18px"',
    'padding: "12px 14px"'
)

text = text.replace(
    'fontSize: 28,',
    'fontSize: 24,'
)

text = text.replace(
    'fontSize: 22,',
    'fontSize: 18,'
)

text = text.replace(
    'border: "1px solid rgba(56,189,248,.18)"',
    'border: "1px solid rgba(56,189,248,.12)"'
)

PAGE.write_text(text, encoding="utf-8")

print("STEP_273_EXECUTION_WORKSPACE_REDESIGN_INSTALLED")
print(f"Backup: {backup}")
print("STEP_273_OK")