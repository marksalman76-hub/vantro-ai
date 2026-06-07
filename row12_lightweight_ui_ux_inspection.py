from pathlib import Path

files = [
    "frontend/src/app/admin/page.tsx",
    "frontend/src/app/client/page.tsx",
    "frontend/src/app/signup/page.tsx",
    "frontend/src/app/activate/page.tsx",
    "frontend/src/app/billing/page.tsx",
    "frontend/src/app/support/page.tsx",
]

terms = [
    "TODO",
    "FIXME",
    "placeholder",
    "lorem",
    "dummy",
    "mock",
    "test only",
    "demo only",
    "coming soon",
    "undefined",
    "null",
    "internal",
    "governance",
    "runtime",
    "debug",
    "console.log",
    "alert(",
    "temporary",
    "beta",
]

print("ROW12_LIGHTWEIGHT_UI_UX_INSPECTION")

for file_path in files:
    path = Path(file_path)
    print("")
    print("===", file_path, "===")

    if not path.exists():
        print("MISSING_FILE")
        continue

    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    print("chars", len(text), "lines", len(lines))

    hits = []
    for line_number, line in enumerate(lines, 1):
        lowered = line.lower()
        for term in terms:
            if term.lower() in lowered:
                hits.append((line_number, term, line.strip()[:220]))
                break

    if not hits:
        print("NO_LIGHTWEIGHT_POLISH_FLAGS")
        continue

    for line_number, term, line in hits[:120]:
        print(f"L{line_number}: [{term}] {line}")

    if len(hits) > 120:
        print("TRUNCATED_HITS", len(hits))