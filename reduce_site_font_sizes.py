from pathlib import Path
from datetime import datetime
import re

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
backup_dir = root / "backups" / f"font_reduction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

targets = [
    root / "frontend" / "src" / "app" / "page.tsx",
    root / "frontend" / "src" / "app" / "signup" / "page.tsx",
    root / "frontend" / "src" / "app" / "support-request" / "page.tsx",
    root / "frontend" / "src" / "app" / "about" / "page.tsx",
    root / "frontend" / "src" / "app" / "blog" / "page.tsx",
    root / "frontend" / "src" / "app" / "demo" / "page.tsx",
]

def reduce_px(match):
    value = int(match.group(1))
    if value <= 12:
        new_value = value
    elif value <= 16:
        new_value = max(12, round(value * 0.94))
    elif value <= 28:
        new_value = max(14, round(value * 0.88))
    else:
        new_value = max(22, round(value * 0.78))
    return f"{new_value}px"

def reduce_font_size_number(match):
    value = int(match.group(1))
    if value <= 12:
        new_value = value
    elif value <= 16:
        new_value = max(12, round(value * 0.94))
    elif value <= 28:
        new_value = max(14, round(value * 0.88))
    else:
        new_value = max(22, round(value * 0.78))
    return f"fontSize: {new_value}"

changed = []

for file in targets:
    if not file.exists():
        continue

    original = file.read_text(encoding="utf-8")
    backup = backup_dir / file.relative_to(root)
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text(original, encoding="utf-8")

    updated = original

    updated = re.sub(r"(?<=font-size:\s)(\d+)px", reduce_px, updated)
    updated = re.sub(r"fontSize:\s*(\d+)", reduce_font_size_number, updated)

    if updated != original:
        file.write_text(updated, encoding="utf-8")
        changed.append(str(file.relative_to(root)))

print("SITE_FONT_SIZES_REDUCED")
print("Changed files:")
for item in changed:
    print("-", item)
print("Backup:", backup_dir)