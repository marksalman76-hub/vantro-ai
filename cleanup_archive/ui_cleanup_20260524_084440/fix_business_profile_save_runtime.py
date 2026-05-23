from pathlib import Path
from datetime import datetime
import re

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup = backup_dir / f"client_page_before_business_profile_save_runtime_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

pattern = re.compile(
    r'const saveBusinessProfile = async \(\) => \{.*?\n\s*\};',
    re.DOTALL
)

replacement = '''const saveBusinessProfile = async () => {
    try {
      const cleanedProfile = {
        ...businessProfile,
        business_name: (businessProfile.business_name || "").trim(),
      };

      localStorage.setItem(
        "client_business_profile",
        JSON.stringify(cleanedProfile)
      );

      setBusinessProfile(cleanedProfile);
      setBusinessProfileSaved(true);

      setToastMessage("Business profile saved successfully.");
    } catch (error) {
      console.error("Business profile save failed", error);
      setToastMessage("Business profile could not be saved.");
    }
  };'''

if not pattern.search(text):
    raise SystemExit("Could not find saveBusinessProfile function.")

text = pattern.sub(replacement, text, count=1)

path.write_text(text, encoding="utf-8")

print("BUSINESS_PROFILE_SAVE_RUNTIME_FIXED")
print(f"Backup: {backup}")