from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
ROUTE = ROOT / "frontend" / "src" / "app" / "api" / "admin-deployment-control" / "route.ts"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = BACKUPS / f"admin_deployment_proxy_before_env_alignment_{timestamp}.ts"
shutil.copy2(ROUTE, backup)

text = ROUTE.read_text(encoding="utf-8")

old = '''const ADMIN_TOKEN =
  process.env.ADMIN_AUTH_TOKEN ||
  process.env.ADMIN_BEARER_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";'''

new = '''const ADMIN_TOKEN =
  process.env.ADMIN_AUTH_SECRET ||
  process.env.ADMIN_AUTH_TOKEN ||
  process.env.ADMIN_BEARER_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";'''

text = text.replace(old, new)

ROUTE.write_text(text, encoding="utf-8")

print("ADMIN_PROXY_ENV_ALIGNMENT_FIXED")
print(f"Backup: {backup}")