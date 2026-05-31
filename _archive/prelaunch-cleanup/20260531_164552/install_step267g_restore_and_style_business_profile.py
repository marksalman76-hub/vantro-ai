from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Backup current broken file before restoring
broken_backup = BACKUPS / f"client_page_broken_before_step267g_{timestamp}.tsx"
broken_backup.write_text(PAGE.read_text(encoding="utf-8"), encoding="utf-8")

# Restore latest working backup from before Step 267F
candidates = sorted(BACKUPS.glob("client_page_before_step267f_*.tsx"))
if not candidates:
    raise SystemExit("ERROR: No Step 267F backup found.")

restore_file = candidates[-1]
text = restore_file.read_text(encoding="utf-8")

# Add a global local class for the business profile textarea fields
style_block = """
      <style jsx>{`
        .business-profile-field {
          width: 100%;
          min-height: 110px;
          border-radius: 18px;
          border: 1px solid rgba(255, 255, 255, 0.12);
          background: rgba(2, 6, 23, 0.72);
          color: #ffffff;
          padding: 16px;
          font-size: 14px;
          outline: none;
          resize: vertical;
        }
        .business-profile-field::placeholder {
          color: rgba(148, 163, 184, 0.85);
        }
        .business-profile-field:focus {
          border-color: rgba(103, 232, 249, 0.65);
          box-shadow: 0 0 0 1px rgba(103, 232, 249, 0.25);
        }
      `}</style>
"""

if "business-profile-field" not in text:
    marker = "BUSINESS PROFILE INTELLIGENCE"
    marker_pos = text.find(marker)
    if marker_pos == -1:
        raise SystemExit("ERROR: Business Profile panel not found after restore.")

    section_start = text.rfind("<section", 0, marker_pos)
    if section_start == -1:
        raise SystemExit("ERROR: Business Profile section start not found.")

    text = text[:section_start] + style_block + "\n" + text[section_start:]

# Only update textareas inside the Business Profile panel
start = text.find("BUSINESS PROFILE INTELLIGENCE")
end = text.find("CLIENT WORKSPACE", start)

if start == -1 or end == -1:
    raise SystemExit("ERROR: Could not find Business Profile panel boundaries.")

before = text[:start]
panel = text[start:end]
after = text[end:]

panel = re.sub(
    r'<textarea\s+className="[^"]*"',
    '<textarea className="business-profile-field"',
    panel
)

text = before + panel + after

PAGE.write_text(text, encoding="utf-8")

print("STEP_267G_RESTORED_AND_STYLED_BUSINESS_PROFILE")
print(f"Broken backup: {broken_backup}")
print(f"Restored from: {restore_file}")
print(f"Updated: {PAGE}")
print("STEP_267G_OK")