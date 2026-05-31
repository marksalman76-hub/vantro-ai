
from pathlib import Path

text = Path("frontend/src/app/api/delegated-workforce-execution/route.ts").read_text(encoding="utf-8")

assert '"x-tenant-id": body.tenant_id || "owner_admin"' in text
assert 'tenant_id: body.tenant_id || "owner_admin"' in text
assert 'connected_integrations: body.connected_integrations || []' in text

print("DELEGATED_PROXY_TENANT_FORWARDING_TEST_PASSED")
