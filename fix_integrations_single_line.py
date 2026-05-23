from pathlib import Path
from datetime import datetime
import re

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_integrations_single_line_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

# Force the integrations container to stay in one horizontal line.
text = re.sub(
    r'(<section[^>]*>\s*<div[^>]*>\s*<h2[^>]*>\s*Integrations\s*</h2>[\s\S]*?</section>)',
    lambda m: m.group(1)
        .replace('flexWrap: "wrap"', 'flexWrap: "nowrap"')
        .replace('gridTemplateColumns: "repeat(auto-fit,minmax(160px,1fr))"', 'gridTemplateColumns: "repeat(7, minmax(120px, 1fr))"')
        .replace('gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))"', 'gridTemplateColumns: "repeat(7, minmax(120px, 1fr))"')
        .replace('overflow: "hidden"', 'overflow: "visible"'),
    text,
    count=1,
)

# Make integration cards more compact so all items fit on one line.
text = text.replace('minWidth: 180', 'minWidth: 132')
text = text.replace('minWidth: 170', 'minWidth: 132')
text = text.replace('padding: "14px 16px"', 'padding: "10px 12px"')
text = text.replace('padding: "12px 14px"', 'padding: "10px 12px"')

# Make Add Integration compact too.
text = text.replace('padding: "12px 16px"', 'padding: "10px 12px"')

path.write_text(text, encoding="utf-8")

print("INTEGRATIONS_SINGLE_LINE_FIXED")
print(f"Backup: {backup}")