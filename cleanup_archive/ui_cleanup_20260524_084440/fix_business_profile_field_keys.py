from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

text = PAGE.read_text(encoding="utf-8")

backup = BACKUP_DIR / f"client_page_before_business_profile_field_keys_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

old = '''            {[
              ["Business niche", "Describe your business niche, product category, and market position"],
              ["Products & services", "Main products, bundles, offers"],
              ["Target audience", "Customer type, location, needs"],
              ["Competitors", "Competitor names, websites, market examples"],
              ["Offers", "Current promotions, bundles, guarantees"],
              ["Brand voice", "Premium, playful, clinical, bold, friendly"],
              ["Positioning", "Why customers should choose you"],
              ["Goals", "Sales, launches, retention, growth"],
            ].map(([label, value]) => ('''

new = '''            {[
              ["business_niche", "Business niche", "Describe your business niche, product category, and market position"],
              ["products_services", "Products & services", "Main products, bundles, offers"],
              ["target_audience", "Target audience", "Customer type, location, needs"],
              ["competitors", "Competitors", "Competitor names, websites, market examples"],
              ["offers", "Offers", "Current promotions, bundles, guarantees"],
              ["brand_voice", "Brand voice", "Premium, playful, clinical, bold, friendly"],
              ["notes", "Positioning", "Why customers should choose you"],
              ["goals", "Goals", "Sales, launches, retention, growth"],
            ].map(([key, label, value]) => ('''

if old not in text:
    raise SystemExit("BUSINESS_PROFILE_FIELD_ARRAY_NOT_FOUND")

text = text.replace(old, new, 1)
text = text.replace(
    'value={businessProfile[key] || ""} onChange={(e) => setBusinessProfile((prev) => ({ ...prev, [key]: e.target.value }))}',
    'value={businessProfile[String(key)] || ""} onChange={(e) => setBusinessProfile((prev) => ({ ...prev, [String(key)]: e.target.value }))}',
)

PAGE.write_text(text, encoding="utf-8")

print("BUSINESS_PROFILE_FIELD_KEYS_FIXED")
print(f"Backup: {backup}")