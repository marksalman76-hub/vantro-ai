from pathlib import Path
import subprocess

ROOT = Path.cwd()
route = ROOT / "frontend" / "src" / "app" / "api" / "logout" / "route.ts"
text = route.read_text(encoding="utf-8", errors="ignore")

checks = {
    "logout_route_exists": route.exists(),
    "get_handler_present": "export async function GET" in text,
    "post_handler_present": "export async function POST" in text,
    "redirect_uses_303": "status: 303" in text,
    "cookie_cleared": 'maxAge: 0' in text,
}

print("LIVE_LOGOUT_GET_405_FIX_RESULTS")
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

print("LIVE_LOGOUT_GET_405_FIX_OK")
