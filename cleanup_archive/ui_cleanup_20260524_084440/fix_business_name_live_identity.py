from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_business_name_live_identity_{stamp}.tsx"
shutil.copy2(PAGE, backup)

text = PAGE.read_text(encoding="utf-8")

old_display = '''  const clientDisplayName =
    businessProfileAny?.business_name ||
    businessProfileAny?.company_name ||
    businessProfileAny?.brand_name ||
    businessProfileAny?.business_niche ||
    accountAny?.company_name ||
    accountAny?.business_name ||
    accountAny?.client_name ||
    accountAny?.contact_name ||
    accountAny?.full_name ||
    accountAny?.email ||
    "Client";'''

new_display = '''  const typedBusinessName = String(businessProfile.business_name || "").trim();
  const clientDisplayName =
    typedBusinessName ||
    businessProfileAny?.company_name ||
    businessProfileAny?.brand_name ||
    accountAny?.company_name ||
    accountAny?.business_name ||
    accountAny?.client_name ||
    accountAny?.contact_name ||
    accountAny?.full_name ||
    accountAny?.email ||
    "Client";'''

if old_display not in text:
    raise RuntimeError("clientDisplayName block not found. No changes written.")

text = text.replace(old_display, new_display, 1)

# Make Business name visually clearer in the existing generated textarea loop.
old_business_field = '''["business_name", "◆", "Business name", "Your company, store, or brand name", "normal"],'''
new_business_field = '''["business_name", "◆", "Business name", "Type your company, store, or brand name here", "normal"],'''

if old_business_field in text:
    text = text.replace(old_business_field, new_business_field, 1)

# Add a clear note above the business profile grid.
grid_anchor = '''          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, minmax(0, 1fr))", gap: 12 }}>'''

note = '''          <div style={{ marginBottom: 12, borderRadius: 14, border: "1px solid rgba(79,70,229,.12)", background: "rgba(238,242,255,.45)", padding: "10px 12px", color: "#334155", fontSize: 12.4, fontWeight: 750 }}>
            Start with <strong>Business name</strong>. This controls the client initials and account name shown in the top-right profile menu.
          </div>

''' + grid_anchor

if grid_anchor not in text:
    raise RuntimeError("Business profile grid anchor not found.")

if "This controls the client initials and account name" not in text:
    text = text.replace(grid_anchor, note, 1)

PAGE.write_text(text, encoding="utf-8")

print("BUSINESS_NAME_LIVE_IDENTITY_FIXED")
print(f"Backup: {backup}")