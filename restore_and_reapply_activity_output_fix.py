from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"

latest_backup = sorted(
    BACKUPS.glob("client_page_before_activity_output_polish_*.tsx")
)

if not latest_backup:
    raise SystemExit("ERROR: No pre-polish backup found.")

restore_file = latest_backup[-1]

broken_backup = BACKUPS / f"broken_page_after_failed_activity_polish_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, broken_backup)

shutil.copy2(restore_file, PAGE)

print("PAGE_RESTORED_SUCCESSFULLY")
print("Restored from:", restore_file)
print("Broken version archived to:", broken_backup)