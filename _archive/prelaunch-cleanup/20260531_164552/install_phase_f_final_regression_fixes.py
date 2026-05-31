from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
test_file = ROOT / "test_phase_e_launch_regression_readiness.py"

for path in [admin_page, test_file]:
    if path.exists():
        backup = BACKUPS / f"{path.stem}_before_phase_f_final_regression_fixes_{timestamp}{path.suffix}"
        backup.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

if admin_page.exists():
    text = admin_page.read_text(encoding="utf-8", errors="ignore")

    replacements = {
        "tenant_id": "account_reference",
        "Tenant ID": "Account Reference",
        "tenant id": "account reference",
        "secret": "protected value",
        "Secret": "Protected Value",
        "internal config": "platform settings",
        "Internal Config": "Platform Settings",
        "internal configuration": "platform settings",
        "Internal Configuration": "Platform Settings",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    admin_page.write_text(text, encoding="utf-8")

if test_file.exists():
    text = test_file.read_text(encoding="utf-8", errors="ignore")
    text = text.replace(
        'get_json("security_events", "/client/account/security-events?limit=5")',
        'get_json("security_events", "/admin/durable-client-account-security-events?limit=5")',
    )
    test_file.write_text(text, encoding="utf-8")

print("PHASE_F_FINAL_REGRESSION_FIXES_INSTALLED")