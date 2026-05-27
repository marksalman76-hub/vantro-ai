from pathlib import Path
import subprocess

ROOT = Path.cwd()
client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
text = client_page.read_text(encoding="utf-8", errors="ignore").lower()

checks = {
    "client_page_exists": client_page.exists(),
    "business_profile_panel_present": "business profile" in text,
    "niche_field_present": "niche / category" in text,
    "products_field_present": "products / services" in text,
    "audience_field_present": "target audience" in text,
    "competitors_field_present": "competitors" in text,
    "offers_field_present": "current offers" in text,
    "regions_field_present": "regions / countries" in text,
    "brand_tone_field_present": "brand tone" in text,
    "goals_field_present": "main goals" in text,
    "business_profile_sent_to_run_agent": "business_profile: businessprofile" in text,
}

print("STEP_267_CLIENT_BUSINESS_PROFILE_UI_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

print("RUNNING_FRONTEND_BUILD")
build = subprocess.run(["npm.cmd", "run", "build"], cwd=str(ROOT / "frontend"), text=True)
print("frontend_build_exit_code", build.returncode)

if build.returncode != 0:
    failed.append("frontend_build")

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_267_CLIENT_BUSINESS_PROFILE_UI_OK")
