from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
s = p.read_text(encoding="utf-8")

markers = [
    "StepHeader",
    "Execution deliverables",
    "Quick Actions",
    "Governed execution, every time.",
    "responsiveWorkspaceGridStyle",
    "Run Agent",
]

out = []

for marker in markers:
    out.append(f"\n\n========== MARKER: {marker} ==========")
    positions = []
    start = 0
    while True:
        i = s.find(marker, start)
        if i == -1:
            break
        positions.append(i)
        start = i + len(marker)

    out.append(f"COUNT: {len(positions)}")
    for idx, pos in enumerate(positions[:10], 1):
        out.append(f"\n--- OCCURRENCE {idx} AT {pos} ---")
        out.append(s[max(0, pos - 1800):min(len(s), pos + 2600)])

Path("client_page_structure_report.txt").write_text("\n".join(out), encoding="utf-8")
print("WROTE client_page_structure_report.txt")