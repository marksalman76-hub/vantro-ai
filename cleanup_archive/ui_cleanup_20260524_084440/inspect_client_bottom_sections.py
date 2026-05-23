from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")
lower = text.lower()

keywords = [
    "Activity",
    "Latest governed activity",
    "Client deliverables",
    "Execution Output Viewer",
    "Media preview unavailable",
    "Approve",
    "Reject",
    "View full deliverable",
    "Expand preview",
]

print("CLIENT_BOTTOM_SECTIONS_INSPECTION")

for keyword in keywords:
    idx = lower.find(keyword.lower())
    print("\n" + "=" * 90)
    print("KEYWORD:", keyword)
    print("FOUND_INDEX:", idx)
    if idx != -1:
        start = max(0, idx - 2600)
        end = min(len(text), idx + 6200)
        print(text[start:end])

print("\nCLIENT_BOTTOM_SECTIONS_INSPECTION_OK")