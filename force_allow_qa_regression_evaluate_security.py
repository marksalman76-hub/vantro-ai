from pathlib import Path
from datetime import datetime

path = Path("backend/app/core/security_audit_enforcement_runtime.py")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups") / ("force_allow_qa_regression_evaluate_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "security_audit_enforcement_runtime.py"
backup.write_text(text, encoding="utf-8")

route_block = '''
def _is_qa_regression_evaluate_path(path: str) -> bool:
    return str(path or "").rstrip("/") == "/admin/qa-regression-intelligence/evaluate"
'''

if "_is_qa_regression_evaluate_path" not in text:
    insert_after = 'def _is_admin_path(path: str) -> bool:'
    idx = text.find(insert_after)
    if idx == -1:
        raise SystemExit("ADMIN_PATH_FUNCTION_NOT_FOUND")
    text = text[:idx] + route_block + "\n\n" + text[idx:]

needle = 'path = request.url.path'
idx = text.find(needle)
if idx == -1:
    raise SystemExit("REQUEST_PATH_LINE_NOT_FOUND")

guard = '''
        if _is_qa_regression_evaluate_path(path) and method == "POST" and _admin_token_valid(request):
            return await call_next(request)
'''

if "_is_qa_regression_evaluate_path(path) and method == \"POST\"" not in text:
    line_end = text.find("\n", idx)
    text = text[:line_end + 1] + guard + text[line_end + 1:]

path.write_text(text, encoding="utf-8")

print("QA_REGRESSION_EVALUATE_FORCE_ALLOWED")
print("Backup:", backup)