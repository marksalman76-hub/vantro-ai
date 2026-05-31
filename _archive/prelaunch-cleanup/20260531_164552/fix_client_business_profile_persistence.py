from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_business_profile_persistence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

old = '''  async function loadBusinessProfile() {
    try {
      const response = await fetch("/api/client-business-profile", { cache: "no-store" });
      const data = await response.json();

      if (data?.success && data.profile) {
        setBusinessProfile(data.profile);
        setBusinessProfileSaved(Boolean(data.profile_saved));
      }
    } catch {
      setBusinessProfileSaved(false);
    }
  }'''

new = '''  async function loadBusinessProfile() {
    try {
      const localProfileRaw = window.localStorage.getItem("client_business_profile");
      const localProfile = localProfileRaw ? JSON.parse(localProfileRaw) : null;

      const response = await fetch("/api/client-business-profile", {
        cache: "no-store",
        credentials: "include",
      });

      const data = await response.json();

      if (data?.success && data.profile && Object.keys(data.profile).length > 0) {
        const mergedProfile = {
          ...(localProfile || {}),
          ...data.profile,
        };

        setBusinessProfile(mergedProfile);
        setBusinessProfileSaved(Boolean(data.profile_saved || mergedProfile.business_name));
        window.localStorage.setItem("client_business_profile", JSON.stringify(mergedProfile));
        return;
      }

      if (localProfile && Object.keys(localProfile).length > 0) {
        setBusinessProfile(localProfile);
        setBusinessProfileSaved(Boolean(localProfile.business_name));
        return;
      }

      setBusinessProfileSaved(false);
    } catch {
      try {
        const localProfileRaw = window.localStorage.getItem("client_business_profile");
        const localProfile = localProfileRaw ? JSON.parse(localProfileRaw) : null;

        if (localProfile && Object.keys(localProfile).length > 0) {
          setBusinessProfile(localProfile);
          setBusinessProfileSaved(Boolean(localProfile.business_name));
          return;
        }
      } catch {}

      setBusinessProfileSaved(false);
    }
  }'''

if old not in s:
    raise SystemExit("FAILED: loadBusinessProfile block not found")

s = s.replace(old, new, 1)

old = '''      setBusinessProfile(savedProfile);
      setBusinessProfileSaved(true);
      localStorage.setItem("client_business_profile", JSON.stringify(savedProfile));
      setToastMessage("Business profile saved successfully.");'''

new = '''      setBusinessProfile(savedProfile);
      setBusinessProfileSaved(true);
      window.localStorage.setItem("client_business_profile", JSON.stringify(savedProfile));
      setToastMessage("Business profile saved successfully.");'''

if old in s:
    s = s.replace(old, new, 1)

old = '''{account?.company_name || account?.contact_email || "Client Workspace"}'''
new = '''{clientDisplayName || account?.company_name || account?.contact_email || "Client Workspace"}'''

if old in s:
    s = s.replace(old, new, 1)

TARGET.write_text(s, encoding="utf-8")

print("CLIENT_BUSINESS_PROFILE_PERSISTENCE_FIXED")
print(f"Backup: {backup}")