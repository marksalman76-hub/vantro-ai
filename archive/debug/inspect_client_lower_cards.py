from pathlib import Path

s = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")

terms = [
    "Execution",
    "Deliverable",
    "Preview",
    "Asset",
    "Generated",
    "Result",
    "output",
    "runtime",
    "Open",
    "No asset",
]

out = []
for term in terms:
    idx = s.lower().find(term.lower())
    if idx != -1:
        out.append(f"\n\n================ {term} ================\n")
        out.append(s[max(0, idx - 2500): idx + 4500])

Path("client_lower_cards_inspection.txt").write_text("".join(out), encoding="utf-8")
print("WROTE client_lower_cards_inspection.txt")