from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
main_file = ROOT / "backend" / "app" / "main.py"

if not main_file.exists():
    raise SystemExit("backend/app/main.py not found")

backups = ROOT / "backups"
backups.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = backups / f"main_before_safe_live_auth_fingerprint_{timestamp}.py"
backup_file.write_text(main_file.read_text(encoding="utf-8"), encoding="utf-8")

content = main_file.read_text(encoding="utf-8")

import_block = """
import os
import hashlib
"""

if "import hashlib" not in content:
    if "import os" in content:
        content = content.replace("import os", "import os\nimport hashlib", 1)
    else:
        content = import_block.strip() + "\n" + content

route_block = r'''

@app.get("/debug/live-auth-fingerprint")
def debug_live_auth_fingerprint():
    def fp(name: str):
        value = os.getenv(name, "").strip()
        return {
            "present": bool(value),
            "length": len(value),
            "sha_prefix": hashlib.sha256(value.encode()).hexdigest()[:10] if value else None,
        }

    return {
        "success": True,
        "safe_debug": True,
        "secrets_not_returned": True,
        "admin_platform_token": fp("ADMIN_PLATFORM_TOKEN"),
        "admin_auth_secret": fp("ADMIN_AUTH_SECRET"),
        "admin_auth_token": fp("ADMIN_AUTH_TOKEN"),
        "app_env": os.getenv("APP_ENV", ""),
        "service": "control-api",
    }
'''

if "/debug/live-auth-fingerprint" not in content:
    content = content.rstrip() + "\n" + route_block.strip() + "\n"

main_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_safe_live_auth_fingerprint_import.py"
test_file.write_text(r'''
from backend.app.main import app

routes = [getattr(route, "path", "") for route in app.routes]

assert "/debug/live-auth-fingerprint" in routes

print("SAFE_LIVE_AUTH_FINGERPRINT_IMPORT_OK")
'''.strip() + "\n", encoding="utf-8")

print("SAFE_LIVE_AUTH_FINGERPRINT_ADDED")
print(f"Backup: {backup_file}")
print(f"Updated: {main_file}")
print(f"Created: {test_file}")