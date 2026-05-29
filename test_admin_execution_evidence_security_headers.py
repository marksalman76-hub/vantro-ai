
from pathlib import Path

text = Path("frontend/src/app/api/admin-execution-evidence/route.ts").read_text(encoding="utf-8")

assert '"Authorization": `Bearer ${ADMIN_TOKEN}`' in text
assert '"x-csrf-token": "admin-execution-evidence"' in text
assert '"origin": process.env.NEXT_PUBLIC_FRONTEND_URL || "https://app.trance-formation.com.au"' in text
assert '"x-actor-role": "owner_admin"' in text
assert '"x-tenant-id": tenantId || "owner_admin"' in text

print("ADMIN_EXECUTION_EVIDENCE_SECURITY_HEADERS_TEST_PASSED")
