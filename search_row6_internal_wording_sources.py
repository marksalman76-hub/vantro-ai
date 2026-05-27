from pathlib import Path

terms = [
    "internal_prompt_exposure_blocked",
    "backend_architecture_exposure_blocked",
]

roots = [
    Path("backend"),
    Path("frontend"),
    Path("services"),
]

suffixes = {".py", ".ts", ".tsx", ".json", ".jsonl", ".txt"}

for term in terms:
    print("\nTERM:", term)

    found_any = False

    for root in roots:
        if not root.exists():
            continue

        for p in root.rglob("*"):
            if not p.is_file():
                continue

            if p.suffix.lower() not in suffixes:
                continue

            try:
                s = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            if term in s:
                found_any = True
                print("-", p)

    if not found_any:
        print("- no source file matches")

print("\nDATA SEARCH")

data_root = Path("backend/app/data")

for term in terms:
    print("\nTERM:", term)

    found_any = False

    if data_root.exists():
        for p in data_root.rglob("*"):
            if not p.is_file():
                continue

            try:
                s = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            if term in s:
                found_any = True
                print("-", p)

    if not found_any:
        print("- no data file matches")