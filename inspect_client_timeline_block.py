from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")
lower = text.lower()

keywords = [
    "execution timeline",
    "live governed execution events connected",
    "execution completed",
    "executionEvents",
    "timeline",
]

print("CLIENT_TIMELINE_BLOCK_INSPECTION")

for keyword in keywords:
    idx = lower.find(keyword.lower())
    print("\n" + "=" * 80)
    print("KEYWORD:", keyword)
    print("FOUND_INDEX:", idx)
    if idx != -1:
        start = max(0, idx - 2500)
        end = min(len(text), idx + 4500)
        snippet = text[start:end]
        print(snippet)

print("\nCLIENT_TIMELINE_BLOCK_INSPECTION_OK")