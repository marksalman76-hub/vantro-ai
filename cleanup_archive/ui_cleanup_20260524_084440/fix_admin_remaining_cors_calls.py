from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = BACKUPS / f"admin_page_before_final_cors_fix_{timestamp}.tsx"
shutil.copy2(PAGE, backup)

text = PAGE.read_text(encoding="utf-8")

# Force ALL deployment-control fetches through proxy
text = re.sub(
    r'fetch\(`?\s*https?://[^`"]+/admin/deployment-control/([^`"]+)`?',
    r'fetch("/api/admin-deployment-control"',
    text
)

text = text.replace(
    'body: JSON.stringify(payload),',
    'body: JSON.stringify({ path, method: "POST", payload }),'
)

# Hard-fix list endpoint
text = re.sub(
    r'fetch\(\s*["\'].*?/admin/deployment-control/list\?limit=25["\']',
    'fetch("/api/admin-deployment-control"',
    text
)

# Hard-fix summary endpoint
text = re.sub(
    r'fetch\(\s*["\'].*?/admin/deployment-control/summary["\']',
    'fetch("/api/admin-deployment-control"',
    text
)

# Inject correct list body if missing
if '/admin/deployment-control/list?limit=25' not in text:
    text = text.replace(
        'cache: "no-store",',
        '''method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          path: "/admin/deployment-control/list?limit=25",
          method: "GET"
        }),''',
        1
    )

# Inject correct summary body if missing
if '/admin/deployment-control/summary' not in text:
    text = text.replace(
        'cache: "no-store",',
        '''method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          path: "/admin/deployment-control/summary",
          method: "GET"
        }),''',
        1
    )

PAGE.write_text(text, encoding="utf-8")

print("FINAL_ADMIN_CORS_FIX_COMPLETE")
print(f"Backup: {backup}")