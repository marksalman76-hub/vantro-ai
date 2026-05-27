from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"provider_execution_http_exception_fix_before_{STAMP}"

MAIN = ROOT / "backend" / "app" / "main.py"

if not MAIN.exists():
    raise FileNotFoundError(f"Missing backend main.py: {MAIN}")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
backup_target = BACKUP_DIR / "backend" / "app" / "main.py"
backup_target.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(MAIN, backup_target)

text = MAIN.read_text(encoding="utf-8")

if "raise HTTPException(status_code=401" not in text:
    raise RuntimeError("Expected governed action HTTPException block was not found.")

text = text.replace(
    "raise HTTPException(status_code=401, detail=\"Unauthorised provider execution action\")",
    "raise _ProviderActionHTTPException(status_code=401, detail=\"Unauthorised provider execution action\")",
)

text = text.replace(
    "raise HTTPException(status_code=400, detail=\"job_id is required\")",
    "raise _ProviderActionHTTPException(status_code=400, detail=\"job_id is required\")",
)

if "from fastapi import HTTPException as _ProviderActionHTTPException" not in text:
    marker = "# --- Provider execution governed admin actions ---"
    if marker not in text:
        raise RuntimeError("Provider execution governed actions marker not found.")
    text = text.replace(
        marker,
        marker + "\nfrom fastapi import HTTPException as _ProviderActionHTTPException",
        1,
    )

MAIN.write_text(text, encoding="utf-8")

print("PROVIDER_EXECUTION_HTTP_EXCEPTION_FIX_APPLIED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {MAIN}")