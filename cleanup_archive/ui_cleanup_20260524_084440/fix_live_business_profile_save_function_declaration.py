from pathlib import Path
from datetime import datetime
import re

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_save_function_declaration_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

pattern = re.compile(
    r'async function saveBusinessProfile\(\) \{[\s\S]*?\n  \}',
    re.MULTILINE
)

replacement = '''async function saveBusinessProfile() {
    try {
      const cleanedProfile = {
        ...businessProfile,
        business_name: (businessProfile.business_name || "").trim(),
      };

      const response = await fetch("/api/client-business-profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ profile: cleanedProfile }),
      });

      const result = await response.json().catch(() => ({
        success: false,
        error: "invalid_json_response",
      }));

      if (!response.ok || !result?.success) {
        console.error("Business profile save failed", result);
        setToastMessage(
          result?.error
            ? `Business profile save failed: ${result.error}`
            : "Business profile could not be saved."
        );
        return;
      }

      const savedProfile =
        result?.profile && typeof result.profile === "object"
          ? result.profile
          : cleanedProfile;

      setBusinessProfile(savedProfile);
      setBusinessProfileSaved(true);
      localStorage.setItem("client_business_profile", JSON.stringify(savedProfile));
      setToastMessage("Business profile saved successfully.");
    } catch (error) {
      console.error("Business profile save runtime failure", error);
      setToastMessage("Business profile could not be saved.");
    }
  }'''

text, count = pattern.subn(replacement, text, count=1)

if count != 1:
    raise SystemExit(f"Expected to replace 1 saveBusinessProfile function, replaced {count}")

path.write_text(text, encoding="utf-8")

print("LIVE_BUSINESS_PROFILE_SAVE_FUNCTION_DECLARATION_FIXED")
print(f"Backup: {backup}")