from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"admin_page_before_duplicate_fetch_options_{timestamp}.tsx"
shutil.copy2(PAGE, backup)

text = PAGE.read_text(encoding="utf-8")

# Collapse duplicate adjacent method lines.
while re.search(r'(\n\s*method:\s*"POST",\s*)\n\s*method:\s*"POST",', text):
    text = re.sub(r'(\n\s*method:\s*"POST",\s*)\n\s*method:\s*"POST",', r'\1', text)

# Collapse duplicate adjacent headers lines.
while re.search(r'(\n\s*headers:\s*\{\s*"Content-Type":\s*"application/json"\s*\},\s*)\n\s*headers:\s*\{\s*"Content-Type":\s*"application/json"\s*\},', text):
    text = re.sub(
        r'(\n\s*headers:\s*\{\s*"Content-Type":\s*"application/json"\s*\},\s*)\n\s*headers:\s*\{\s*"Content-Type":\s*"application/json"\s*\},',
        r'\1',
        text,
    )

# Collapse duplicate adjacent cache lines.
while re.search(r'(\n\s*cache:\s*"no-store",\s*)\n\s*cache:\s*"no-store",', text):
    text = re.sub(r'(\n\s*cache:\s*"no-store",\s*)\n\s*cache:\s*"no-store",', r'\1', text)

PAGE.write_text(text, encoding="utf-8")

print("ADMIN_DUPLICATE_FETCH_OPTIONS_FIXED")
print(f"Backup: {backup}")