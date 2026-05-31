from pathlib import Path

terms = [
    "AI Workforce Platform",
    "Owner Command Centre",
    "Run Agent",
    "Deploy Clients",
    "Client Registry",
]

roots = [
    Path("frontend/src"),
    Path("."),
]

suffixes = {".tsx", ".ts", ".jsx", ".js", ".txt"}

seen = set()

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

        hits = [t for t in terms if t in s]

        if hits and str(p) not in seen:
            seen.add(str(p))
            print(p)
            print("HITS =", hits)
            print("-" * 80)