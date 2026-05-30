from pathlib import Path
from datetime import datetime

main_path = Path("backend/app/main.py")
text = main_path.read_text(encoding="utf-8")

backup_dir = Path("backups") / ("qa_regression_admin_routes_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "main.py"
backup.write_text(text, encoding="utf-8")

import_block = "from backend.app.runtime.autonomous_qa_regression_intelligence import autonomous_qa_regression_status, build_qa_regression_packet\n"
if import_block not in text:
    marker = "from backend.app.runtime.execution_stack import ("
    text = text.replace(marker, import_block + marker, 1)

route_block = '''
# Autonomous QA Regression Intelligence Admin Routes
@app.get("/admin/qa-regression-intelligence/status")
def admin_qa_regression_intelligence_status():
    return autonomous_qa_regression_status()


@app.post("/admin/qa-regression-intelligence/evaluate")
def admin_qa_regression_intelligence_evaluate(payload: dict):
    checks = payload.get("checks") if isinstance(payload, dict) else []
    environment = str(payload.get("environment") or "production") if isinstance(payload, dict) else "production"
    source = str(payload.get("source") or "qa_testing_agent") if isinstance(payload, dict) else "qa_testing_agent"

    return build_qa_regression_packet(
        checks=checks if isinstance(checks, list) else [],
        source=source,
        environment=environment,
    )
'''

if "/admin/qa-regression-intelligence/status" not in text:
    text = text.rstrip() + "\n\n" + route_block + "\n"

main_path.write_text(text, encoding="utf-8")

print("QA_REGRESSION_ADMIN_ROUTES_WIRED")
print("Backup:", backup)