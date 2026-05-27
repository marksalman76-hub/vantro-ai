from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = BACKUPS / f"client_page_backend_api_base_proxy_{stamp}"
backup_dir.mkdir(exist_ok=True)

p = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
s = p.read_text(encoding="utf-8")
(backup_dir / "page.tsx").write_text(s, encoding="utf-8")

old = s

s = s.replace(
    "`${BACKEND_API_BASE}/client/execution-events?tenant_id=${encodeURIComponent(eventTenantId)}&project_id=live_readiness_matrix&limit=20`",
    "`/api/client-execution-matrix?tenant_id=${encodeURIComponent(eventTenantId)}&project_id=live_readiness_matrix&limit=20`",
)

s = s.replace("`${BACKEND_API_BASE}/client/integrations`", "`/api/client-integrations`")
s = s.replace("`${BACKEND_API_BASE}/client/integrations/connect`", "`/api/client-integrations-connect`")
s = s.replace("`${BACKEND_API_BASE}/client/integrations/test`", "`/api/client-integrations-test`")
s = s.replace("`${BACKEND_API_BASE}/client/integrations/disconnect`", "`/api/client-integrations-disconnect`")

p.write_text(s, encoding="utf-8")

print("CLIENT_PAGE_BACKEND_API_BASE_PROXY_FIXED")
print("Backup:", backup_dir)
print("Changed:", s != old)