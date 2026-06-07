from pathlib import Path

targets = {
    "frontend/src/app/page.tsx": [
        "href=",
        "signup",
        "demo",
        "billing",
        "support",
        "Start",
        "Book",
        "Launch",
        "Buy",
        "Get started",
    ],
    "frontend/src/app/signup/page.tsx": [
        "fetch(",
        "billing-checkout",
        "activate",
        "package",
        "agent",
        "selected",
        "error",
    ],
    "frontend/src/app/demo/page.tsx": [
        "href=",
        "signup",
        "support",
        "demo",
        "trial",
        "launch",
    ],
    "frontend/src/app/support-request/page.tsx": [
        "support-agent-chat",
        "fetch(",
        "error",
        "success",
        "governed",
        "internal",
        "runtime",
        "debug",
    ],
    "frontend/src/app/api/support-agent-chat/route.ts": [
        "return",
        "governed",
        "internal",
        "runtime",
        "debug",
        "escalation",
        "billing",
        "technical",
        "account",
    ],
    "frontend/src/app/api/sales-demo-launch-flow-status/route.ts": [
        "return",
        "demo",
        "launch",
        "ready",
        "sales",
        "status",
    ],
}

print("ROW15_TARGETED_LAUNCH_COPY_CTA_CHECK")

for file_path, terms in targets.items():
    path = Path(file_path)
    print("")
    print("===", file_path, "===")

    if not path.exists():
        print("MISSING")
        continue

    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    printed = set()

    for index, line in enumerate(lines, 1):
        lowered = line.lower()
        if any(term.lower() in lowered for term in terms):
            start = max(1, index - 2)
            end = min(len(lines), index + 2)
            key = (start, end)
            if key in printed:
                continue
            printed.add(key)

            print("--- around L" + str(index) + " ---")
            for line_number in range(start, end + 1):
                print("L" + str(line_number) + ": " + lines[line_number - 1])

    if not printed:
        print("NO_TARGETED_HITS")