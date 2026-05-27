from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
s = p.read_text(encoding="utf-8")
i = s.find("Execution output viewer")

if i == -1:
    raise SystemExit("Execution output viewer marker not found.")

Path("current_output_viewer_block.txt").write_text(
    s[max(0, i - 1400):min(len(s), i + 6500)],
    encoding="utf-8",
)

print("WROTE current_output_viewer_block.txt")