from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
s = p.read_text(encoding="utf-8")

markers = [
    "DEFAULT_AGENTS",
    "active_agents",
    "account?.active_agents",
    "package",
    "plan",
    "subscription",
    "Run AI Agent",
]

out = []
for marker in markers:
    out.append(f"\n\n========== {marker} ==========")
    start = 0
    count = 0
    while True:
        i = s.find(marker, start)
        if i == -1:
            break
        count += 1
        out.append(f"\n--- occurrence {count} at {i} ---")
        out.append(s[max(0, i - 900):min(len(s), i + 1600)])
        start = i + len(marker)
    out.append(f"\nCOUNT: {count}")

Path("package_agent_runtime_report.txt").write_text("\n".join(out), encoding="utf-8")
print("WROTE package_agent_runtime_report.txt")