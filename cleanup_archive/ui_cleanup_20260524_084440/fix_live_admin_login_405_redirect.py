from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
LOGIN_ROUTE = ROOT / "frontend" / "src" / "app" / "api" / "login" / "route.ts"
TEST = ROOT / "test_live_admin_login_405_redirect_fix.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"login_route_before_405_redirect_fix_{timestamp}.ts"
backup.write_text(LOGIN_ROUTE.read_text(encoding="utf-8"), encoding="utf-8")

text = LOGIN_ROUTE.read_text(encoding="utf-8")

text = text.replace(
    "const response = NextResponse.redirect(new URL(next, request.url));",
    "const response = NextResponse.redirect(new URL(next, request.url), { status: 303 });"
)

LOGIN_ROUTE.write_text(text, encoding="utf-8")

TEST.write_text(r'''
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

failed = [name for name, passed in checks.items() if not passed)

print("RUNNING_FRONTEND_BUILD")
build = subprocess.run(["npm.cmd", "run", "build"], cwd=str(ROOT / "frontend"), text=True)
print("frontend_build_exit_code", build.returncode)

if build.returncode != 0:
    failed.append("frontend_build")

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("LIVE_ADMIN_LOGIN_405_REDIRECT_FIX_OK")
'''.replace("failed = [name for name, passed in checks.items() if not passed)", "failed = [name for name, passed in checks.items() if not passed]"), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("LIVE_ADMIN_LOGIN_405_REDIRECT_FIX_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {LOGIN_ROUTE}")
print(f"Created/updated: {TEST}")