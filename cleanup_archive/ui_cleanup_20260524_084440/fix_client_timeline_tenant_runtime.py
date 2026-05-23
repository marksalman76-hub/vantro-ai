from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_timeline_tenant_runtime_{timestamp}.tsx"
backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

text = path.read_text(encoding="utf-8")

text = text.replace(
'''  useEffect(() => {
    loadExecutionTimeline();
  }, []);''',
'''  useEffect(() => {
    if (account) {
      loadExecutionTimeline();
    }
  }, [account]);'''
)

text = text.replace(
'''      const response = await fetch(
        `${BACKEND_API_BASE}/client/execution-events?tenant_id=client_manual_admin&project_id=live_readiness_matrix&limit=20`,
        {
          cache: "no-store",
          headers: {
            "x-tenant-id": "client_manual_admin",
            "x-actor-role": "customer",
          },
        }
      );''',
'''      const tenantId =
        account?.tenant_id ||
        account?.client_id ||
        "client_manual_admin";

      const response = await fetch(
        `${BACKEND_API_BASE}/client/execution-events?tenant_id=${encodeURIComponent(tenantId)}&project_id=live_readiness_matrix&limit=20`,
        {
          cache: "no-store",
          headers: {
            "x-tenant-id": tenantId,
            "x-actor-role": "customer",
          },
        }
      );'''
)

path.write_text(text, encoding="utf-8")

print("CLIENT_TIMELINE_TENANT_RUNTIME_FIXED")
print(f"Backup: {backup}")