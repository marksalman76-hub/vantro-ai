from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_cookie_clean_repair_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

# Restore broken JSX style tag to the original safe form.
s = re.sub(
    r"<style>\{CSS \+ `.*?</style>",
    "<style>{CSS}</style>",
    s,
    flags=re.DOTALL,
)

cookie_css = r'''
  .cookieConsent {
    position: fixed;
    left: 24px;
    right: 24px;
    bottom: 24px;
    z-index: 9999;
    max-width: 980px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    padding: 18px 20px;
    border-radius: 22px;
    border: 1px solid rgba(165, 180, 252, 0.28);
    background: linear-gradient(180deg, rgba(8, 13, 28, 0.96), rgba(3, 7, 18, 0.98));
    box-shadow: 0 28px 90px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255,255,255,0.08);
    backdrop-filter: blur(22px) saturate(150%);
    -webkit-backdrop-filter: blur(22px) saturate(150%);
    color: #f8fafc;
  }

  .cookieConsent strong {
    display: block;
    font-size: 15px;
    font-weight: 950;
    margin-bottom: 5px;
  }

  .cookieConsent p {
    margin: 0;
    color: #94a3b8;
    font-size: 13px;
    line-height: 1.45;
    max-width: 680px;
  }

  .cookieConsent__actions {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
  }

  .cookieConsent__actions a {
    color: #c7d2fe;
    font-size: 13px;
    font-weight: 850;
    text-decoration: none;
  }

  .cookieConsent__actions button {
    border: 0;
    border-radius: 14px;
    padding: 11px 14px;
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: #ffffff;
    font-weight: 950;
    cursor: pointer;
    box-shadow: 0 16px 34px rgba(79, 70, 229, 0.32);
  }

  @media (max-width: 720px) {
    .cookieConsent {
      align-items: flex-start;
      flex-direction: column;
    }

    .cookieConsent__actions {
      width: 100%;
      justify-content: space-between;
    }
  }
'''

# Append cookie CSS inside the CSS template constant, not inside JSX.
if ".cookieConsent {" not in s:
    marker = "\n`;\n"
    idx = s.rfind(marker)
    if idx == -1:
        raise SystemExit("FAILED: CSS constant closing marker not found")
    s = s[:idx] + cookie_css + s[idx:]

PAGE.write_text(s, encoding="utf-8")

print("COOKIE_POPUP_CLEAN_REPAIR_DONE")
print(f"Backup: {backup}")