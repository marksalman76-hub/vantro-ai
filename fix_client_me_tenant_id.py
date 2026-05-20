from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/api/client-me/route.ts")
backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_me_route_before_tenant_id_{timestamp}.ts"
backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

text = path.read_text(encoding="utf-8")

text = text.replace(
'''    account: {
      company_name: account.company_name || "Client Workspace",''',
'''    account: {
      tenant_id: account.tenant_id || account.client_id || account.id || "",
      client_id: account.client_id || account.tenant_id || account.id || "",
      company_name: account.company_name || "Client Workspace",'''
)

path.write_text(text, encoding="utf-8")

print("CLIENT_ME_TENANT_ID_EXPOSED")
print(f"Backup: {backup}")