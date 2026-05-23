from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
FILE = ROOT / "backend" / "app" / "core" / "admin_deployment_control_runtime.py"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"admin_deployment_control_runtime_before_postgres_activation_{timestamp}.py"
shutil.copy2(FILE, backup)

text = FILE.read_text(encoding="utf-8")

text = text.replace(
    "from backend.app.core.tenant_account_runtime import create_client_activation_invite\n",
    "from backend.app.core.postgres_account_runtime import create_activation_invite as pg_create_activation_invite\n",
)

text = text.replace(
    "invite = create_client_activation_invite({",
    "invite = pg_create_activation_invite({",
)

FILE.write_text(text, encoding="utf-8")

print("ADMIN_DEPLOY_POSTGRES_ACTIVATION_INVITE_FIXED")
print(f"Backup: {backup}")