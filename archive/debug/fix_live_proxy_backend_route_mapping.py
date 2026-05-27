from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = BACKUPS / f"live_proxy_mapping_fix_{stamp}"
backup_dir.mkdir(exist_ok=True)

routes = {
    "frontend/src/app/api/client-me/route.ts": "/client/me",
    "frontend/src/app/api/client-business-profile/route.ts": "/client/business-profile",
    "frontend/src/app/api/client-execution-matrix/route.ts": "/client/execution-events",
    "frontend/src/app/api/run-agent/route.ts": "/run-agent",
}

for file_path, backend_path in routes.items():
    path = ROOT / file_path

    original = path.read_text(encoding="utf-8")

    backup = backup_dir / path.name
    backup.write_text(original, encoding="utf-8")

    updated = original

    updated = updated.replace('"/api/client-me"', f'"{backend_path}"')
    updated = updated.replace('"/api/client-business-profile"', f'"{backend_path}"')
    updated = updated.replace('"/api/client-execution-matrix"', f'"{backend_path}"')
    updated = updated.replace('"/run-agent"', f'"{backend_path}"')

    path.write_text(updated, encoding="utf-8")

print("LIVE_PROXY_BACKEND_ROUTE_MAPPING_FIXED")
print("Backup:", backup_dir)