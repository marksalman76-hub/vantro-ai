from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_profile_save_local_first_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

old_state = '''const [businessProfile, setBusinessProfile] = useState<Record<string, string>>({});'''
new_state = '''const [businessProfile, setBusinessProfile] = useState<Record<string, string>>(() => {
    if (typeof window === "undefined") return {};
    try {
      const saved = window.localStorage.getItem("client_business_profile");
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });'''

if old_state not in s:
    print("WARNING: businessProfile state already changed or marker not found")
else:
    s = s.replace(old_state, new_state, 1)

old_saved_state = '''const [businessProfileSaved, setBusinessProfileSaved] = useState(false);'''
new_saved_state = '''const [businessProfileSaved, setBusinessProfileSaved] = useState(() => {
    if (typeof window === "undefined") return false;
    try {
      const saved = window.localStorage.getItem("client_business_profile");
      const parsed = saved ? JSON.parse(saved) : null;
      return Boolean(parsed?.business_name);
    } catch {
      return false;
    }
  });'''

if old_saved_state not in s:
    print("WARNING: businessProfileSaved state already changed or marker not found")
else:
    s = s.replace(old_saved_state, new_saved_state, 1)

start = s.find("  async function saveBusinessProfile() {")
end = s.find("\n  async function loadExecutionTimeline()", start)

if start == -1 or end == -1:
    raise SystemExit("FAILED: saveBusinessProfile block not found")

new_save = '''  async function saveBusinessProfile() {
    const cleanedProfile = {
      ...businessProfile,
      business_name: (businessProfile.business_name || "").trim(),
    };

    try {
      window.localStorage.setItem("client_business_profile", JSON.stringify(cleanedProfile));
    } catch {}

    setBusinessProfile(cleanedProfile);
    setBusinessProfileSaved(Boolean(cleanedProfile.business_name));
    setToastMessage("Business profile saved successfully.");

    try {
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
        console.warn("Business profile backend sync failed; local profile remains saved.", result);
        return;
      }

      const savedProfile =
        result?.profile && typeof result.profile === "object"
          ? { ...cleanedProfile, ...result.profile }
          : cleanedProfile;

      setBusinessProfile(savedProfile);
      setBusinessProfileSaved(Boolean(savedProfile.business_name));
      window.localStorage.setItem("client_business_profile", JSON.stringify(savedProfile));
    } catch (error) {
      console.warn("Business profile backend sync failed; local profile remains saved.", error);
    }
  }
'''

s = s[:start] + new_save + s[end:]

TARGET.write_text(s, encoding="utf-8")

print("PROFILE_SAVE_LOCAL_FIRST_FIXED")
print(f"Backup: {backup}")