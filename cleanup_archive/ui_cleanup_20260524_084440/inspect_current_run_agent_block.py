from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
s = p.read_text(encoding="utf-8")

marker = "Select agents and launch governed execution."
i = s.find(marker)

out = Path("current_run_agent_block.txt")

if i == -1:
    out.write_text("MARKER_NOT_FOUND\n", encoding="utf-8")
    print("MARKER_NOT_FOUND")
else:
    start = max(0, i - 3000)
    end = min(len(s), i + 7000)
    out.write_text(s[start:end], encoding="utf-8")
    print("WROTE current_run_agent_block.txt")
    print("START", start)
    print("END", end)