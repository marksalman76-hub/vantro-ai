from pathlib import Path
from datetime import datetime

path = Path("backend/app/core/security_audit_enforcement_runtime.py")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups") / ("qa_regression_post_security_path_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "security_audit_enforcement_runtime.py"
backup.write_text(text, encoding="utf-8")

old = 'ADMIN_EVIDENCE_PROXY_PATHS = ("/admin/execution-evidence",)'
new = 'ADMIN_EVIDENCE_PROXY_PATHS = ("/admin/execution-evidence", "/admin/qa-regression-intelligence/evaluate")'

if old not in text:
    raise SystemExit("ADMIN_EVIDENCE_PROXY_PATHS_TARGET_NOT_FOUND")

path.write_text(text.replace(old, new), encoding="utf-8")

print("QA_REGRESSION_POST_SECURITY_PATH_ALLOWED")
print("Backup:", backup)