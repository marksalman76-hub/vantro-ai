from pathlib import Path

checks = [
    "frontend/src/app/page.tsx",
    "frontend/src/app/admin/page.tsx",
    "frontend/src/app/client/page.tsx",
    "frontend/src/app/signup/page.tsx",
    "frontend/src/app/activate/page.tsx",
    "frontend/src/app/billing/page.tsx",
    "frontend/src/app/support/page.tsx",
    "frontend/src/app/api/billing",
    "frontend/src/app/api/support",
]

print("ROW12_TARGETED_ROUTE_ALERT_CHECK")

for item in checks:
    path = Path(item)
    if path.exists():
        kind = "DIR" if path.is_dir() else "FILE"
        print(item, "EXISTS", kind)
    else:
        print(item, "MISSING")

target_files = [
    "frontend/src/app/admin/page.tsx",
    "frontend/src/app/client/page.tsx",
]

search_terms = [
    "alert(JSON.stringify",
    "alert(",
    "Real generated media",
    "runtime deliverables",
    "Customer-safe proof",
]

for file_path in target_files:
    path = Path(file_path)
    print("")
    print("=== ALERT_CONTEXT", file_path, "===")

    if not path.exists():
        print("MISSING_FILE")
        continue

    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

    for index, line in enumerate(lines, 1):
        if any(term in line for term in search_terms):
            start = max(1, index - 3)
            end = min(len(lines), index + 3)

            print("--- around L" + str(index) + " ---")
            for line_number in range(start, end + 1):
                print("L" + str(line_number) + ": " + lines[line_number - 1])