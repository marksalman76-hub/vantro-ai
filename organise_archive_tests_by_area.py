from pathlib import Path
import shutil

root = Path.cwd()
tests_root = root / "archive" / "tests"

if not tests_root.exists():
    raise SystemExit("archive/tests folder not found")

categories = {
    "runtime": [
        "runtime",
        "execution_stack",
        "run_agent",
        "worker",
        "queue",
        "orchestration",
        "workflow",
        "entitlement",
        "activation",
        "catalogue",
        "credit",
        "tenant",
        "ledger",
        "persistence",
        "database",
        "postgres",
    ],
    "ui": [
        "frontend",
        "client_portal",
        "homepage",
        "admin_",
        "portal",
        "workspace",
        "ux",
        "ui",
        "dashboard",
        "login",
        "logout",
        "signup",
    ],
    "stripe": [
        "stripe",
        "billing",
        "checkout",
        "invoice",
        "subscription",
        "payment",
    ],
    "providers": [
        "provider",
        "openai",
        "llm",
        "ai_media",
        "asset",
        "creative",
        "shopify",
        "brevo",
        "crm",
        "connector",
        "adapter",
    ],
    "security": [
        "security",
        "auth",
        "governance",
        "safe",
        "guard",
        "credential",
        "controlled",
        "fingerprint",
        "single_use",
        "lock",
    ],
}

for category in categories:
    (tests_root / category).mkdir(parents=True, exist_ok=True)

uncategorised = tests_root / "uncategorised"
uncategorised.mkdir(parents=True, exist_ok=True)

moved = 0

for item in list(tests_root.iterdir()):
    if item.is_dir():
        continue

    name = item.name.lower()
    destination_category = None

    for category, keywords in categories.items():
        if any(keyword in name for keyword in keywords):
            destination_category = category
            break

    if destination_category is None:
        destination_category = "uncategorised"

    destination = tests_root / destination_category / item.name

    if destination.exists():
        stem = destination.stem
        suffix = destination.suffix
        i = 2
        while True:
            renamed = tests_root / destination_category / f"{stem}_{i}{suffix}"
            if not renamed.exists():
                destination = renamed
                break
            i += 1

    shutil.move(str(item), str(destination))
    moved += 1

print("ARCHIVE_TESTS_ORGANISED_BY_AREA")
print(f"Moved files: {moved}")
print("Created/used:")
for category in list(categories.keys()) + ["uncategorised"]:
    print(f"- archive/tests/{category}")