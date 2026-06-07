from pathlib import Path

checks = [
    "frontend/src/app/page.tsx",
    "frontend/src/app/signup/page.tsx",
    "frontend/src/app/demo/page.tsx",
    "frontend/src/app/about/page.tsx",
    "frontend/src/app/support-request/page.tsx",
    "frontend/src/app/privacy-policy/page.tsx",
    "frontend/src/app/terms-of-service/page.tsx",
    "frontend/src/app/refund-policy/page.tsx",
    "frontend/src/app/cookies/page.tsx",
    "frontend/src/app/api/billing-checkout/route.ts",
    "frontend/src/app/api/signup-agent-selection/options/[plan]/route.ts",
    "frontend/src/app/api/signup-agent-selection/validate/route.ts",
    "frontend/src/app/api/signup-locked-activation/draft/route.ts",
    "frontend/src/app/api/signup-locked-activation/activate/route.ts",
    "frontend/src/app/api/sales-demo-launch-flow-status/route.ts",
    "frontend/src/app/api/support-agent-chat/route.ts",
]

terms = [
    "TODO",
    "FIXME",
    "coming soon",
    "placeholder",
    "lorem",
    "dummy",
    "mock",
    "test only",
    "demo only",
    "beta",
    "under construction",
    "not implemented",
    "console.log",
    "alert(",
    "undefined",
    "null",
    "internal",
    "runtime",
    "debug",
    "secret",
    "api key",
]

print("ROW15_SALES_LAUNCH_READINESS_INSPECTION")

for file_path in checks:
    path = Path(file_path)
    print("")
    print("===", file_path, "===")

    if not path.exists():
        print("MISSING")
        continue

    kind = "DIR" if path.is_dir() else "FILE"
    print("EXISTS", kind)

    if path.is_dir():
        continue

    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    print("chars", len(text), "lines", len(lines))

    hits = []
    for line_number, line in enumerate(lines, 1):
        lowered = line.lower()
        for term in terms:
            if term.lower() in lowered:
                hits.append((line_number, term, line.strip()[:240]))
                break

    if not hits:
        print("NO_LAUNCH_READINESS_FLAGS")
        continue

    for line_number, term, line in hits[:100]:
        print(f"L{line_number}: [{term}] {line}")

    if len(hits) > 100:
        print("TRUNCATED_HITS", len(hits))