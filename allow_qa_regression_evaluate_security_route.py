from pathlib import Path
from datetime import datetime

path = Path("backend/app/core/security_audit_enforcement_runtime.py")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups") / ("qa_regression_security_allow_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "security_audit_enforcement_runtime.py"
backup.write_text(text, encoding="utf-8")

route = '"/admin/qa-regression-intelligence/evaluate"'

if route not in text:
    marker = "ADMIN_MUTATION_ALLOWLIST = {"
    if marker not in text:
        raise SystemExit("ADMIN_MUTATION_ALLOWLIST_NOT_FOUND")
    text = text.replace(marker, marker + f"\n    {route},", 1)

path.write_text(text, encoding="utf-8")

print("QA_REGRESSION_EVALUATE_SECURITY_ROUTE_ALLOWED")
print("Backup:", backup)