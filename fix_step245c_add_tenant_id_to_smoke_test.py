from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
TEST = ROOT / "test_step245_customer_onboarding_smoke_lock.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = BACKUPS / f"test_step245_before_step245c_{timestamp}.py"
backup.write_text(TEST.read_text(encoding="utf-8"), encoding="utf-8")

text = TEST.read_text(encoding="utf-8")

old = '''invite_payload = {
    "company_name": "Step 245 Smoke Test Store",
    "email": "step245-smoke@example.com",
    "package": "Growth",
    "active_agents": [
        "product_copywriting_agent",
        "ugc_creative_agent",
        "analytics_optimisation_agent",
    ],
}'''

new = '''invite_payload = {
    "tenant_id": "client_step245_smoke",
    "company_name": "Step 245 Smoke Test Store",
    "email": "step245-smoke@example.com",
    "package": "Growth",
    "active_agents": [
        "product_copywriting_agent",
        "ugc_creative_agent",
        "analytics_optimisation_agent",
    ],
}'''

if old not in text:
    raise RuntimeError("invite payload block not found")

text = text.replace(old, new)

TEST.write_text(text, encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_245C_ADD_TENANT_ID_TO_SMOKE_TEST_OK")
print(f"Backup: {backup}")
print(f"Updated: {TEST}")