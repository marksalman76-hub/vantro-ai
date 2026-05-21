from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")
lower = text.lower()

keywords = [
    "run agent",
    "active agents",
    "selectedagents",
    "textarea",
    "task",
]

print("CLIENT_RUN_AGENT_BLOCK_INSPECTION")

for keyword in keywords:
    idx = lower.find(keyword.lower())
    print("\n" + "=" * 80)
    print("KEYWORD:", keyword)
    print("FOUND_INDEX:", idx)
    if idx != -1:
        start = max(0, idx - 2200)
        end = min(len(text), idx + 5200)
        print(text[start:end])

print("\nCLIENT_RUN_AGENT_BLOCK_INSPECTION_OK")