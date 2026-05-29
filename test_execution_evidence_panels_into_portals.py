
from pathlib import Path

admin = Path("frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")
client = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")

assert "Global execution evidence" in admin
assert "/api/admin-execution-evidence?tenant_id=client_demo_001&limit=10" in admin
assert "Brevo live execution" in admin

assert "Execution proof" in client
assert "/api/client-execution-evidence?tenant_id=client_demo_001&limit=10" in client
assert "No credential" in admin

print("EXECUTION_EVIDENCE_PANELS_INTO_PORTALS_TEST_PASSED")
