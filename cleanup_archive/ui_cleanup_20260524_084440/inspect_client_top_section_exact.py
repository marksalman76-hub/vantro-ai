from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
s = p.read_text(encoding="utf-8")

markers = [
    "Select agents and launch governed execution.",
    "Execution pipeline",
    "Execution deliverables",
    "Quick Actions",
]

for marker in markers:
    i = s.find(marker)
    print("\nMARKER:", marker)
    print("INDEX:", i)
    if i != -1:
        start = max(0, i - 2500)
        end = min(len(s), i + 4500)
        print(s[start:end])
        print("\n" + "=" * 100)