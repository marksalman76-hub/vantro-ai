from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_remove_product_footer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

pattern = r'''
\s*\{
\s*title:\s*"Product",
.*?
\},
'''

s = re.sub(pattern, '', s, flags=re.DOTALL | re.VERBOSE)

PAGE.write_text(s, encoding="utf-8")

print("FOOTER_PRODUCT_SECTION_REMOVED")
print(f"Backup: {backup}")