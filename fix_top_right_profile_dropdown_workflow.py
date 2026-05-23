from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_top_right_profile_dropdown_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

old_details = '<details style={{ position: "relative" }}>'
new_details = '<details style={{ position: "relative", zIndex: 100 }}>'

text = text.replace(old_details, new_details, 1)

# Make dropdown profile button scroll to account centre after opening profile.
old_profile_click = '''                  onClick={() => {
                    setActiveAccountPanel("profile");
                    window.location.hash = "profile";
                    
                  }}'''

new_profile_click = '''                  onClick={() => {
                    setActiveAccountPanel("profile");
                    window.location.hash = "profile";
                    window.setTimeout(() => {
                      document.getElementById("account-centre-profile-panel")?.scrollIntoView({
                        behavior: "smooth",
                        block: "start",
                      });
                    }, 50);
                  }}'''

if old_profile_click not in text:
    raise SystemExit("Could not find top-right Profile button click handler.")

text = text.replace(old_profile_click, new_profile_click, 1)

old_section = '<section style={{ ...cardStyle, padding: 18, marginBottom: 18, position: "relative", zIndex: 3 }}>'
new_section = '<section id="account-centre-profile-panel" style={{ ...cardStyle, padding: 18, marginBottom: 18, position: "relative", zIndex: 3 }}>'

if old_section not in text:
    raise SystemExit("Could not find Account Centre section opening tag.")

text = text.replace(old_section, new_section, 1)

path.write_text(text, encoding="utf-8")

print("TOP_RIGHT_PROFILE_DROPDOWN_WORKFLOW_FIXED")
print(f"Backup: {backup}")