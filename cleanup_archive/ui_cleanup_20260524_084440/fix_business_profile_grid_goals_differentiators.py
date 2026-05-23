from pathlib import Path
from datetime import datetime
import re

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_business_profile_goals_differentiators_grid_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

# Make the Business Profile Intelligence field grid a clean 4-column layout.
text = text.replace(
    'gridTemplateColumns: "repeat(auto-fit,minmax(230px,1fr))"',
    'gridTemplateColumns: "repeat(4, minmax(0, 1fr))"'
)

text = text.replace(
    'gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))"',
    'gridTemplateColumns: "repeat(4, minmax(0, 1fr))"'
)

text = text.replace(
    'gridTemplateColumns: "repeat(auto-fit,minmax(240px,1fr))"',
    'gridTemplateColumns: "repeat(4, minmax(0, 1fr))"'
)

text = text.replace(
    'gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))"',
    'gridTemplateColumns: "repeat(4, minmax(0, 1fr))"'
)

# Remove any old full-width treatment from Key differentiators.
text = text.replace('gridColumn: "span 2",', '')
text = text.replace('gridColumn: "1 / -1",', '')

# Add deterministic layout rules to the profile cards by label.
# Goals = left half of final row. Key differentiators = right half of final row.
text = text.replace(
    'label === "Key differentiators"',
    'label === "Key differentiators"'
)

style_marker = 'style={{\n                    ...fieldCardStyle,'
if style_marker not in text:
    raise SystemExit("Could not find business profile field card style marker.")

replacement = '''style={{
                    ...fieldCardStyle,
                    ...(label === "Goals" ? { gridColumn: "1 / span 2" } : {}),
                    ...(label === "Key differentiators" ? { gridColumn: "3 / span 2" } : {}),'''

text = text.replace(style_marker, replacement, 1)

# Ensure Key differentiators appears directly after Goals in the field definition/order.
labels_order = [
    "Business name",
    "Business description",
    "Products & services",
    "Ideal customer",
    "Competitors",
    "Offers",
    "Brand voice",
    "Positioning",
    "Goals",
    "Key differentiators",
]

# Flexible array reorder for common field object structures.
field_array_match = re.search(
    r'(const\s+businessProfileFields\s*=\s*\[)([\s\S]*?)(\];)',
    text
)

if field_array_match:
    prefix, body, suffix = field_array_match.groups()

    objects = re.findall(r'\{[\s\S]*?label:\s*"([^"]+)"[\s\S]*?\},', body)
    if objects:
        chunks = re.findall(r'(\s*\{[\s\S]*?label:\s*"([^"]+)"[\s\S]*?\},)', body)
        chunk_map = {label: chunk for chunk, label in chunks}

        ordered_chunks = []
        used = set()

        for label in labels_order:
            if label in chunk_map:
                ordered_chunks.append(chunk_map[label])
                used.add(label)

        for chunk, label in chunks:
            if label not in used:
                ordered_chunks.append(chunk)

        new_body = "".join(ordered_chunks)
        text = text[:field_array_match.start()] + prefix + new_body + suffix + text[field_array_match.end():]

path.write_text(text, encoding="utf-8")

print("BUSINESS_PROFILE_GOALS_DIFFERENTIATORS_GRID_FIXED")
print(f"Backup: {backup}")