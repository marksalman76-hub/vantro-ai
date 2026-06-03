from pathlib import Path

checks = {
    "frontend/src/lib/packageCreditEnforcement.ts": [
        "evaluatePackageCreditEnforcement",
        "attachPackageCreditEnforcement",
        "consumeExecutionCredit",
        "getRemainingCredits",
        "owner_admin_bypass",
        "package_credit_enforcement_enabled",
        "credit-ledger.json",
        "Owner/admin execution is not limited",
    ],
    "frontend/src/app/api/package-credit-enforcement-status/route.ts": [
        "evaluatePackageCreditEnforcement",
        "package_credit_enforcement_enabled",
    ],
    "frontend/src/app/api/admin-package-credit-enforcement-status/route.ts": [
        "Admin authorisation required",
        "owner_admin_unrestricted",
        "credential_values_exposed: false",
    ],
    "frontend/src/app/api/delegated-workforce-execution/route.ts": [
        "attachPackageCreditEnforcement",
        "packageCreditEnforcement",
    ],
    "frontend/src/app/api/run-agent/route.ts": [
        "attachPackageCreditEnforcement",
        "package_credit_enforcement_enabled",
    ],
}

missing = {}

for file, needles in checks.items():
    path = Path(file)
    if not path.exists():
        missing[file] = ["FILE_MISSING"]
        continue
    text = path.read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW14_PACKAGE_CREDIT_ENFORCEMENT_FAILED missing={missing}")

print("ROW14_PACKAGE_CREDIT_ENFORCEMENT_PASSED")
