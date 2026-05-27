from pathlib import Path
import subprocess

ROOT = Path.cwd()

admin_page = ROOT / "frontend" / "src" / "app" / "admin-login" / "page.tsx"
admin_login = ROOT / "frontend" / "src" / "app" / "api" / "admin-login" / "route.ts"
admin_logout = ROOT / "frontend" / "src" / "app" / "api" / "admin-logout" / "route.ts"
middleware = ROOT / "frontend" / "src" / "middleware.ts"

combined = "\n".join([
    admin_page.read_text(encoding="utf-8", errors="ignore"),
    admin_login.read_text(encoding="utf-8", errors="ignore"),
    admin_logout.read_text(encoding="utf-8", errors="ignore"),
    middleware.read_text(encoding="utf-8", errors="ignore"),
])

checks = {
    "admin_login_page_uses_dedicated_route": 'action="/api/admin-login"' in combined,
    "admin_login_post_present": "export async function POST" in admin_login.read_text(encoding="utf-8"),
    "admin_login_get_present": "export async function GET" in admin_login.read_text(encoding="utf-8"),
    "admin_logout_get_present": "export async function GET" in admin_logout.read_text(encoding="utf-8"),
    "admin_logout_post_present": "export async function POST" in admin_logout.read_text(encoding="utf-8"),
    "redirect_303_present": "status: 303" in combined,
    "middleware_allows_admin_login_api": "/api/admin-login" in combined,
    "middleware_protects_admin": 'pathname.startsWith("/admin")' in combined,
    "portal_access_code_used": "PORTAL_ACCESS_CODE" in combined,
}

print("LIVE_ADMIN_ACCESS_FLOW_FIX_RESULTS")
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

print("LIVE_ADMIN_ACCESS_FLOW_FIX_OK")
