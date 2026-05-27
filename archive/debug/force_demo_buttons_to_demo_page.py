from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_force_demo_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

s = s.replace('<a href="#" className="nav__btn-primary">', '<a href="/demo" className="nav__btn-primary">')
s = s.replace('<a href="#" className="nav__btn-primary nav__btn-primary--mobile">', '<a href="/demo" className="nav__btn-primary nav__btn-primary--mobile">')
s = s.replace('<a href="#" className="hero__cta">', '<a href="/demo" className="hero__cta">')
s = s.replace('<a href="#" className="btn btn--primary">', '<a href="/demo" className="btn btn--primary">')

PAGE.write_text(s, encoding="utf-8")

print("DEMO_BUTTONS_FORCED_TO_DEMO_PAGE")
print(f"Backup: {backup}")