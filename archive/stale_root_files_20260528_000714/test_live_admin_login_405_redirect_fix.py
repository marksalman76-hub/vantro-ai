
from pathlib import Path
import subprocess

ROOT = Path.cwd()
route = ROOT / "frontend" / "src" / "app" / "api" / "login" / "route.ts"
text = route.read_text(encoding="utf-8", errors="ignore")

checks = {
    "login_route_exists": route.exists(),
    "post_handler_present": "export async function POST" in text,
    "redirect_uses_303": "status: 303" in text,
    "portal_access_code_used": "PORTAL_ACCESS_CODE" in text,
    "secure_cookie_present": "secure: true" in text,
}

print("LIVE_ADMIN_LOGIN_405_REDIRECT_FIX_RESULTS")
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

print("LIVE_ADMIN_LOGIN_405_REDIRECT_FIX_OK")
