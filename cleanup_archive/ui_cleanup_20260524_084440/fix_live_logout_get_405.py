from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
LOGOUT_ROUTE = ROOT / "frontend" / "src" / "app" / "api" / "logout" / "route.ts"
TEST = ROOT / "test_live_logout_get_405_fix.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"logout_route_before_get_405_fix_{timestamp}.ts"

if LOGOUT_ROUTE.exists():
    backup.write_text(LOGOUT_ROUTE.read_text(encoding="utf-8"), encoding="utf-8")

LOGOUT_ROUTE.write_text(r'''
import { NextRequest, NextResponse } from "next/server";

function logoutResponse(request: NextRequest) {
  const response = NextResponse.redirect(new URL("/admin-login", request.url), {
    status: 303,
  });

  response.cookies.set("portal_access", "", {
    httpOnly: true,
    secure: true,
    sameSite: "strict",
    path: "/",
    maxAge: 0,
  });

  return response;
}

export async function GET(request: NextRequest) {
  return logoutResponse(request);
}

export async function POST(request: NextRequest) {
  return logoutResponse(request);
}
'''.lstrip(), encoding="utf-8")

TEST.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("LIVE_LOGOUT_GET_405_FIX_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {LOGOUT_ROUTE}")
print(f"Created/updated: {TEST}")