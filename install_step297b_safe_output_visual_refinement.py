from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step297b_safe_visual_refinement_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

replacements = [
    ('LUXE\\n                  <br />\\n                  LAUNCH', 'SKIN\\n                  <br />\\n                  SERUM'),
    ('Premium campaign\\n                  preview', 'Campaign asset\\n                  preview'),
    ('fontSize: 15,', 'fontSize: 13,'),
    ('letterSpacing: 1.2,', 'letterSpacing: 0.8,'),
    ('width: 112,', 'width: 96,'),
    ('height: 112,', 'height: 96,'),
    ('borderRadius: 28,', 'borderRadius: 999,'),
    ('fontSize: 14,', 'fontSize: 13,'),
]

for old, new in replacements:
    text = text.replace(old, new)

PAGE.write_text(text, encoding="utf-8")

print("STEP_297B_SAFE_OUTPUT_VISUAL_REFINEMENT_INSTALLED")
print(f"Backup: {backup}")
print("STEP_297B_OK")