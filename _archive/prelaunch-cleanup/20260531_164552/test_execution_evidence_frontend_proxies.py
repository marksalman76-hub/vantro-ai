
from pathlib import Path

admin = Path("frontend/src/app/api/admin-execution-evidence/route.ts").read_text(encoding="utf-8")
client = Path("frontend/src/app/api/client-execution-evidence/route.ts").read_text(encoding="utf-8")

assert "/admin/execution-evidence" in admin
assert '"x-actor-role": "owner_admin"' in admin
assert '"x-tenant-id": tenantId || "owner_admin"' in admin
assert "credential_values_exposed: false" in admin

assert "/client/execution-evidence" in client
assert '"x-tenant-id": tenantId' in client
assert "credential_values_exposed: false" in client

print("EXECUTION_EVIDENCE_FRONTEND_PROXIES_TEST_PASSED")
