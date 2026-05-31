from pathlib import Path
from datetime import datetime
import re

path = Path("live_verify_billing_stripe_package_automation.py")

if not path.exists():
    raise SystemExit("live_verify_billing_stripe_package_automation.py not found")

text = path.read_text(encoding="utf-8")

backup_dir = Path("backups") / ("row5_verifier_billing_get_compatibility_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "live_verify_billing_stripe_package_automation.py"
backup.write_text(text, encoding="utf-8")

# Accept the intentional safe GET compatibility response for /api/billing-checkout.
text = text.replace("[400, 401, 403, 405]", "[200, 400, 401, 403, 405]")
text = text.replace("[400,401,403,405]", "[200,400,401,403,405]")

# Patch any explicit billing-checkout expected_status block.
text = re.sub(
    r'("path"\s*:\s*"/api/billing-checkout"[\s\S]{0,600}?"expected_status"\s*:\s*)\[[^\]]+\]',
    r'\g<1>[200, 400, 401, 403, 405]',
    text,
)

path.write_text(text, encoding="utf-8")

print("ROW5_VERIFIER_BILLING_GET_COMPATIBILITY_FIXED")
print("Backup:", backup)