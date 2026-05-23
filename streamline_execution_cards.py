from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_streamline_execution_cards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

# Reduce large lower card spacing.
text = text.replace('padding: "28px"', 'padding: "22px"')
text = text.replace('padding: "26px"', 'padding: "22px"')
text = text.replace('gap: 18,', 'gap: 14,')

# Make agent buttons more compact.
text = text.replace('padding: "11px 14px"', 'padding: "8px 12px"')
text = text.replace('padding: "10px 14px"', 'padding: "8px 12px"')
text = text.replace('borderRadius: 14,', 'borderRadius: 12,')
text = text.replace('fontSize: 14,', 'fontSize: 13,')

# Reduce task box height.
text = text.replace('minHeight: 190,', 'minHeight: 150,')
text = text.replace('minHeight: 180,', 'minHeight: 145,')
text = text.replace('height: 190,', 'height: 150,')

# Reduce Run Agent button height/spacing.
text = text.replace('height: 64,', 'height: 52,')
text = text.replace('minHeight: 64,', 'minHeight: 52,')
text = text.replace('padding: "18px 20px"', 'padding: "14px 18px"')

# Make execution flow more compact.
text = text.replace('gap: 24,', 'gap: 14,')
text = text.replace('gap: 22,', 'gap: 14,')
text = text.replace('marginTop: 24,', 'marginTop: 14,')
text = text.replace('marginBottom: 24,', 'marginBottom: 14,')

# Reduce numbered circles in execution flow.
text = text.replace('width: 42,', 'width: 34,')
text = text.replace('height: 42,', 'height: 34,')
text = text.replace('width: 44,', 'width: 34,')
text = text.replace('height: 44,', 'height: 34,')

# If the active agents list is one column, make it two-column compact.
text = text.replace(
    'display: "grid",\n                  gridTemplateColumns: "1fr",',
    'display: "grid",\n                  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",'
)

text = text.replace(
    'display: "grid",\n                gridTemplateColumns: "1fr",',
    'display: "grid",\n                gridTemplateColumns: "repeat(2, minmax(0, 1fr))",'
)

path.write_text(text, encoding="utf-8")

print("EXECUTION_CARDS_STREAMLINED")
print(f"Backup: {backup}")