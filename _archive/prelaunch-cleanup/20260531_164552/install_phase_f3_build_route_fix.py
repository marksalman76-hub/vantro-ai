from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
test_file = ROOT / "test_phase_e_launch_regression_readiness.py"

for path in [admin_page, test_file]:
    backup = BACKUPS / f"{path.stem}_before_phase_f3_build_route_fix_{timestamp}{path.suffix}"
    backup.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

text = admin_page.read_text(encoding="utf-8", errors="ignore")
text = text.replace(".protected value_exposure_detected", ".secret_exposure_detected")
text = text.replace("protected value_exposure_detected", "secret_exposure_detected")
admin_page.write_text(text, encoding="utf-8")

test = test_file.read_text(encoding="utf-8", errors="ignore")
test = test.replace(
    'get_json("security_events", "/admin/durable-client-account-security-events?limit=5")',
    'get_json("security_events", "/admin/client-account-security-events?limit=5")',
)
test_file.write_text(test, encoding="utf-8")

print("PHASE_F3_BUILD_ROUTE_FIX_INSTALLED")