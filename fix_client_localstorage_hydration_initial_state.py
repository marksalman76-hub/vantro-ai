from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
text = p.read_text(encoding="utf-8")

old_profile = '''  const [businessProfile, setBusinessProfile] = useState<Record<string, string>>(() => {
    if (typeof window === "undefined") return {};
    try {
      const saved = window.localStorage.getItem("client_business_profile");
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });'''

new_profile = '''  const [businessProfile, setBusinessProfile] = useState<Record<string, string>>({});'''

old_saved = '''  const [businessProfileSaved, setBusinessProfileSaved] = useState(() => {
    if (typeof window === "undefined") return false;
    try {
      const saved = window.localStorage.getItem("client_business_profile");
      const parsed = saved ? JSON.parse(saved) : null;
      return Boolean(parsed?.business_name);
    } catch {
      return false;
    }
  });'''

new_saved = '''  const [businessProfileSaved, setBusinessProfileSaved] = useState(false);'''

old_dark = '''  const [darkModeEnabled, setDarkModeEnabled] = useState(() => {
    if (typeof window === "undefined") return false;
    return window.localStorage.getItem("client_workspace_dark_mode") === "dark";
  });'''

new_dark = '''  const [darkModeEnabled, setDarkModeEnabled] = useState(false);'''

for old, new, label in [
    (old_profile, new_profile, "businessProfile"),
    (old_saved, new_saved, "businessProfileSaved"),
    (old_dark, new_dark, "darkModeEnabled"),
]:
    if old not in text:
        raise SystemExit(f"{label} initialiser block not found")
    text = text.replace(old, new, 1)

p.write_text(text, encoding="utf-8")
print("CLIENT_LOCALSTORAGE_HYDRATION_INITIAL_STATE_FIXED")