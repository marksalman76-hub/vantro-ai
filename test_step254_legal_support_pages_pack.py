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
