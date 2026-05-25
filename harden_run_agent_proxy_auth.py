from pathlib import Path
from datetime import datetime
import shutil

TARGET = Path("frontend/src/app/api/run-agent/route.ts")
content = TARGET.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup_file = backup_dir / f"run_agent_route_before_backend_auth_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ts"
shutil.copy2(TARGET, backup_file)

content = content.replace(
'''const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";''',
'''const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

const BACKEND_AUTH_TOKEN =
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.ADMIN_AUTH_SECRET ||
  process.env.ADMIN_AUTH_TOKEN ||
  process.env.BACKEND_AUTH_TOKEN ||
  "";'''
)

content = content.replace(
'''      headers: {
        "Content-Type": "application/json",
        "x-tenant-id": String(tenantId),
        "x-actor-role": String(actorRole),
      },''',
'''      headers: {
        "Content-Type": "application/json",
        "x-tenant-id": String(tenantId),
        "x-actor-role": String(actorRole),
        ...(BACKEND_AUTH_TOKEN
          ? { Authorization: `Bearer ${BACKEND_AUTH_TOKEN}` }
          : {}),
      },'''
)

TARGET.write_text(content, encoding="utf-8")

print("RUN_AGENT_PROXY_BACKEND_AUTH_HARDENED")
print("Backup:", backup_file)