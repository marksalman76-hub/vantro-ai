from pathlib import Path
from datetime import datetime

main_path = Path("backend/app/main.py")
text = main_path.read_text(encoding="utf-8")

backup_dir = Path("backups") / ("post_deploy_validation_status_route_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "main.py"
backup.write_text(text, encoding="utf-8")

import_line = "from backend.app.runtime.post_deploy_validation_readiness import post_deploy_validation_status\n"
if import_line not in text:
    marker = "from backend.app.runtime.execution_stack import ("
    text = text.replace(marker, import_line + marker, 1)

route_block = '''
# Post-Deploy Validation Readiness Admin Status Route
@app.get("/admin/post-deploy-validation/status")
def admin_post_deploy_validation_status():
    return post_deploy_validation_status()
'''

if "/admin/post-deploy-validation/status" not in text:
    text = text.rstrip() + "\n\n" + route_block + "\n"

main_path.write_text(text, encoding="utf-8")

print("POST_DEPLOY_VALIDATION_STATUS_ROUTE_WIRED")
print("Backup:", backup)