from pathlib import Path

p = Path("backend/app/main.py")
s = p.read_text(encoding="utf-8")

backup = Path("backups/main_before_priority10_billing_import_fix.py")
backup.parent.mkdir(exist_ok=True)
backup.write_text(s, encoding="utf-8")

insert_after = "from backend.app.core.final_deployment_readiness_runtime import final_deployment_readiness"

missing_imports = '''
from backend.app.core.stripe_advanced_billing_runtime import advanced_billing_readiness
from backend.app.core.stripe_customer_billing_portal import billing_portal_readiness
'''

if "advanced_billing_readiness" not in s.split(insert_after)[0]:
    if insert_after not in s:
        raise SystemExit("IMPORT_INSERT_MARKER_NOT_FOUND")
    s = s.replace(insert_after, insert_after + missing_imports, 1)

p.write_text(s, encoding="utf-8")

print("PRIORITY10_BILLING_IMPORTS_FIXED")
print("Backup:", backup)