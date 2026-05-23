from pathlib import Path
from datetime import datetime
import re

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_no_goal_drop_grid_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

# Force the compact 5-column grid so Goals does NOT drop down.
text = text.replace(
    'gridTemplateColumns: "repeat(4, minmax(0, 1fr))"',
    'gridTemplateColumns: "repeat(5, minmax(0, 1fr))"',
    1,
)

# Stop Key differentiators from spanning and pushing layout down.
text = text.replace(
    'gridColumn: label === "Key differentiators" ? "span 3" : "span 1",',
    'gridColumn: "span 1",',
    1,
)

text = text.replace(
    'gridColumn: size === "wide" ? "span 2" : "span 1",',
    'gridColumn: "span 1",',
    1,
)

# Reorder the business profile field array so Goals and Key differentiators are both on the second row.
old_array = '''{[
              ["business_name", "◆", "Business name", "Type business name here", "input", "normal"],
              ["business_niche", "▦", "Business niche", "Describe your business niche, product category, and market position", "textarea", "normal"],
              ["products_services", "◇", "Products & services", "Main products, bundles, offers", "textarea", "normal"],
              ["target_audience", "♙", "Target audience", "Customer type, location, needs", "textarea", "normal"],
              ["competitors", "♕", "Competitors", "Competitor names, websites, market examples", "textarea", "normal"],
              ["offers", "⌑", "Offers", "Current promotions, bundles, guarantees", "textarea", "normal"],
              ["brand_voice", "◁", "Brand voice", "Premium, playful, clinical, bold, friendly", "textarea", "normal"],
              ["positioning", "◎", "Positioning", "Why customers should choose you", "textarea", "normal"],
              ["goals", "⚑", "Goals", "Sales, launches, retention, growth", "textarea", "normal"],
              ["notes", "◌", "Key differentiators", "What makes your business unique? Benefits, values, or competitive advantages.", "textarea", "wide"],
            ].map(([key, icon, label, placeholder, fieldType, size]) => ('''

new_array = '''{[
              ["business_name", "◆", "Business name", "Type business name here", "input", "normal"],
              ["business_niche", "▦", "Business niche", "Describe your business niche, product category, and market position", "textarea", "normal"],
              ["products_services", "◇", "Products & services", "Main products, bundles, offers", "textarea", "normal"],
              ["target_audience", "♙", "Target audience", "Customer type, location, needs", "textarea", "normal"],
              ["competitors", "♕", "Competitors", "Competitor names, websites, market examples", "textarea", "normal"],
              ["offers", "⌑", "Offers", "Current promotions, bundles, guarantees", "textarea", "normal"],
              ["brand_voice", "◁", "Brand voice", "Premium, playful, clinical, bold, friendly", "textarea", "normal"],
              ["positioning", "◎", "Positioning", "Why customers should choose you", "textarea", "normal"],
              ["goals", "⚑", "Goals", "Sales, launches, retention, growth", "textarea", "normal"],
              ["notes", "◌", "Key differentiators", "What makes your business unique? Benefits, values, or competitive advantages.", "textarea", "normal"],
            ].map(([key, icon, label, placeholder, fieldType, size]) => ('''

if old_array not in text:
    raise SystemExit("Could not find exact business profile field array.")

text = text.replace(old_array, new_array, 1)

path.write_text(text, encoding="utf-8")

print("NO_GOAL_DROP_BUSINESS_PROFILE_GRID_FIXED")
print(f"Backup: {backup}")