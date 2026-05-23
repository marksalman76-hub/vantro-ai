from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

text = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_compact_business_profile_pills_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

text = text.replace('gridTemplateColumns: "1fr 1fr 1fr 1.25fr",', 'gridTemplateColumns: "repeat(3, minmax(170px, 1fr)) 1.35fr",')
text = text.replace('padding: "12px 14px",\n                  minHeight: 56,', 'padding: "10px 14px",\n                  minHeight: 44,')
text = text.replace('padding: "12px 14px",\n                  minHeight: 56,', 'padding: "10px 14px",\n                  minHeight: 44,')
text = text.replace('padding: "12px 14px",\n                  minHeight: 56,', 'padding: "10px 14px",\n                  minHeight: 44,')
text = text.replace('fontSize: 13,', 'fontSize: 12.5,', 3)

text = text.replace('padding: "4px 4px 4px 16px",', 'padding: "2px 4px 2px 14px",')
text = text.replace('fontSize: 13.5', 'fontSize: 12.8')
text = text.replace('fontSize: 12, lineHeight: 1.42', 'fontSize: 11.8, lineHeight: 1.35')
text = text.replace('marginTop: 5, color: businessProfileSaved', 'marginTop: 4, color: businessProfileSaved')

text = text.replace('marginTop: 10,\n                borderRadius: 12,', 'marginTop: 8,\n                borderRadius: 12,')
text = text.replace('padding: "9px 12px",', 'padding: "8px 12px",')

PAGE.write_text(text, encoding="utf-8")

print("COMPACT_BUSINESS_PROFILE_ACTION_PILLS_APPLIED")
print(f"Backup: {backup}")