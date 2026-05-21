from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = MAIN.read_text(encoding="utf-8")

backup = BACKUP_DIR / f"main_before_priority5_security_fix_{timestamp}.py"
backup.write_text(text, encoding="utf-8")

import_line = "from backend.app.core.security_hardening_runtime import install_security_hardening, security_hardening_readiness\n"

if import_line not in text:
    marker = "\napp = FastAPI"
    idx = text.find(marker)
    if idx == -1:
        marker = "\napp=FastAPI"
        idx = text.find(marker)
    if idx == -1:
        raise RuntimeError("Could not find FastAPI app marker.")

    text = text[:idx] + "\n" + import_line + text[idx:]

if "install_security_hardening(app)" not in text:
    marker = "app.add_middleware("
    idx = text.find(marker)
    if idx != -1:
        text = text[:idx] + "install_security_hardening(app)\n" + text[idx:]
    else:
        marker = "app.include_router("
        idx = text.find(marker)
        if idx == -1:
            raise RuntimeError("Could not find safe middleware/router insertion point.")
        text = text[:idx] + "install_security_hardening(app)\n" + text[idx:]

route = '''
@app.get("/admin/security-hardening-readiness")
def admin_security_hardening_readiness():
    return security_hardening_readiness()
'''

if "/admin/security-hardening-readiness" not in text:
    text = text.rstrip() + "\n\n" + route + "\n"

MAIN.write_text(text, encoding="utf-8")

print("PRIORITY5_SECURITY_HARDENING_MAIN_FIXED")
print(f"Backup: {backup}")