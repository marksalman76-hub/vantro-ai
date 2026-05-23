from pathlib import Path
from datetime import datetime
import re

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_force_streamlined_run_agent_card_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

start = text.find("Active agents")
end = text.find("Run Agent", start)

if start == -1 or end == -1:
    raise SystemExit("Could not locate Run AI Agent active agents block.")

block_start = text.rfind("<div", 0, start)
block_end = text.find("</button>", end)

if block_start == -1 or block_end == -1:
    raise SystemExit("Could not locate Run AI Agent block boundaries.")

block_end += len("</button>")
block = text[block_start:block_end]

# Force any one-column grid/flex agent list inside this block into compact two-column layout.
block = block.replace(
    'gridTemplateColumns: "1fr"',
    'gridTemplateColumns: "repeat(2, minmax(0, 1fr))"'
)

block = block.replace(
    'gridTemplateColumns: "repeat(1, minmax(0, 1fr))"',
    'gridTemplateColumns: "repeat(2, minmax(0, 1fr))"'
)

# Add compact scroll handling to the agent list wrapper nearest selectedAgents.map.
map_marker = "selectedAgents.map"
map_index = block.find(map_marker)

if map_index != -1:
    style_start = block.rfind("style={{", 0, map_index)
    style_end = block.find("}}", style_start)

    if style_start != -1 and style_end != -1:
        style_body = block[style_start:style_end]

        additions = [
            'display: "grid",',
            'gridTemplateColumns: "repeat(2, minmax(0, 1fr))",',
            'gap: 8,',
            'maxHeight: 260,',
            'overflowY: "auto",',
            'paddingRight: 4,',
        ]

        for item in additions:
            key = item.split(":")[0].strip()
            if key not in style_body:
                style_body += "\n                  " + item

        block = block[:style_start] + style_body + block[style_end:]

# Compact buttons/cards in this block.
block = block.replace('padding: "11px 14px"', 'padding: "8px 10px"')
block = block.replace('padding: "10px 14px"', 'padding: "8px 10px"')
block = block.replace('padding: "12px 14px"', 'padding: "8px 10px"')
block = block.replace('borderRadius: 14', 'borderRadius: 11')
block = block.replace('fontSize: 14', 'fontSize: 12.5')
block = block.replace('minHeight: 190', 'minHeight: 140')
block = block.replace('minHeight: 180', 'minHeight: 140')
block = block.replace('height: 64', 'height: 52')
block = block.replace('minHeight: 64', 'minHeight: 52')

# Compact task panel if present.
block = block.replace('minHeight: 210,', 'minHeight: 150,')
block = block.replace('minHeight: 200,', 'minHeight: 150,')
block = block.replace('minHeight: 190,', 'minHeight: 150,')
block = block.replace('minHeight: 180,', 'minHeight: 150,')

text = text[:block_start] + block + text[block_end:]

path.write_text(text, encoding="utf-8")

print("RUN_AGENT_CARD_FORCE_STREAMLINED")
print(f"Backup: {backup}")