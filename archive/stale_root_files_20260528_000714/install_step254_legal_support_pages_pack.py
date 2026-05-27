from pathlib import Path
from datetime import datetime
import json
import py_compile

ROOT = Path.cwd()
DOCS = ROOT / "docs" / "legal"
DATA = ROOT / "backend" / "app" / "data"
TEST = ROOT / "test_step254_legal_support_pages_pack.py"

DOCS.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

pages = {
    "terms-of-service.md": "# Terms of Service\n\nDraft template. Legal review required before public launch.\n\n## Service\nThis platform provides ecommerce AI agent tools, automation support, content generation, workflow assistance, and business operations support.\n\n## Customer Responsibilities\nCustomers are responsible for reviewing outputs, approving actions, complying with applicable laws, and ensuring submitted data is accurate.\n\n## AI Output\nAI outputs may contain errors and must be reviewed before use.\n\n## Payments\nSubscriptions are billed through Stripe according to the selected package.\n\n## Cancellation\nCustomers may cancel according to the active subscription terms.\n",
    "privacy-policy.md": "# Privacy Policy\n\nDraft template. Legal review required before public launch.\n\n## Data Collected\nWe may collect account, billing, usage, business, and workflow information needed to operate the platform.\n\n## Use of Data\nData is used to provide, secure, improve, and support the service.\n\n## Third Parties\nThe platform may use providers such as hosting, payment, analytics, AI, and integration services.\n\n## Security\nReasonable technical and operational safeguards are used to protect customer data.\n",
    "refund-cancellation-policy.md": "# Refund and Cancellation Policy\n\nDraft template. Legal review required before public launch.\n\n## Monthly Subscription\nSubscriptions are month-to-month unless otherwise agreed.\n\n## Failed Payments\nFailed payments may restrict access until resolved.\n\n## Cancellation\nCancellation stops future renewals according to billing terms.\n\n## Refunds\nRefund eligibility should be reviewed case-by-case according to published policy and applicable law.\n",
    "acceptable-use-policy.md": "# Acceptable Use Policy\n\nDraft template. Legal review required before public launch.\n\nCustomers must not use the platform for unlawful activity, spam, deceptive practices, harmful automation, credential misuse, rights infringement, or prohibited content.\n\nAccounts may be suspended or cancelled for abuse, payment issues, security risk, or policy violations.\n",
    "ai-output-disclaimer.md": "# AI Output Disclaimer\n\nDraft template. Legal review required before public launch.\n\nAI-generated content, recommendations, analysis, and automation outputs are provided for assistance only. Customers must review and approve outputs before publishing, spending, scaling, or making business decisions.\n",
    "support-contact-policy.md": "# Support and Contact Policy\n\nDraft template. Legal review required before public launch.\n\n## Support Channels\nSupport is provided through the approved support email or contact channel.\n\n## Billing Support\nBilling issues should include account email, company name, and subscription package.\n\n## Escalations\nSuspended, cancelled, or blocked accounts may require owner/admin review.\n",
}

for filename, content in pages.items():
    (DOCS / filename).write_text(content, encoding="utf-8")

record = {
    "success": True,
    "step": 254,
    "status": "legal_support_pages_pack_locked",
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "pages": list(pages.keys()),
    "legal_review_required": True,
    "public_launch_gate": {
        "draft_pages_created": True,
        "lawyer_review_required_before_public_launch": True,
    },
}

record_file = DATA / "step254_legal_support_pages_pack.json"
record_file.write_text(json.dumps(record, indent=2), encoding="utf-8")

TEST.write_text(r'''
import json
from pathlib import Path

ROOT = Path.cwd()
DOCS = ROOT / "docs" / "legal"
record = json.loads((ROOT / "backend" / "app" / "data" / "step254_legal_support_pages_pack.json").read_text(encoding="utf-8"))

required = [
    "terms-of-service.md",
    "privacy-policy.md",
    "refund-cancellation-policy.md",
    "acceptable-use-policy.md",
    "ai-output-disclaimer.md",
    "support-contact-policy.md",
]

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "legal_support_pages_pack_locked",
    "all_pages_created": all((DOCS / name).exists() for name in required),
    "legal_review_required": record.get("legal_review_required") is True,
    "launch_gate_present": record.get("public_launch_gate", {}).get("draft_pages_created") is True,
}

print("STEP_254_LEGAL_SUPPORT_PAGES_PACK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]
if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_254_LEGAL_SUPPORT_PAGES_PACK_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_254_LEGAL_SUPPORT_PAGES_PACK_INSTALLED")
print(f"Created folder: {DOCS}")
print(f"Created/updated: {record_file}")
print(f"Created/updated: {TEST}")
print("STEP_254_OK")