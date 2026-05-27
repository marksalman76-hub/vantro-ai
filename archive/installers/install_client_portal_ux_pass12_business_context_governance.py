from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_ux_pass12_business_context_governance_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
original = text
backup.write_text(original, encoding="utf-8")

old = '''Add business context once so every active AI agent can adapt outputs, recommendations, workflows, and execution to the client’s business, market, goals, and operating style.'''

new = '''Add business context once so every active AI agent can adapt outputs, recommendations, workflows, and execution to the client’s business, market, goals, and operating style.

Subscription governance: this business context is licensed for one business only. It cannot be reused across multiple businesses, brands, clients, or unrelated entities under the same subscription.'''

if old not in text:
    raise RuntimeError("Business context description not found")

text = text.replace(old, new, 1)

if "client_portal_business_context_subscription_governance" not in text:
    text = text.replace(
        "// client_portal_aligned_upper_ui_locked",
        "// client_portal_aligned_upper_ui_locked\n// client_portal_business_context_subscription_governance"
    )

if text == original:
    raise RuntimeError("No Pass 12 changes applied.")

PAGE.write_text(text, encoding="utf-8")

TEST = ROOT / "test_client_portal_ux_pass12_business_context_governance.py"
TEST.write_text(r'''
from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS12_BUSINESS_CONTEXT_GOVERNANCE_RESULTS")

checks = {
    "marker": "client_portal_business_context_subscription_governance" in text,
    "governance_copy": "licensed for one business only" in text,
    "no_multiple_businesses": "multiple businesses, brands, clients, or unrelated entities" in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS12_BUSINESS_CONTEXT_GOVERNANCE_OK")
'''.lstrip(), encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS12_BUSINESS_CONTEXT_GOVERNANCE_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print(f"Created: {TEST}")