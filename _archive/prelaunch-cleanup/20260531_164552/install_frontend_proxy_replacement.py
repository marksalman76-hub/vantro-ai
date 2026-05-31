from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
FRONTEND = ROOT / "frontend"
MIDDLEWARE = FRONTEND / "middleware.ts"
SRC_MIDDLEWARE = FRONTEND / "src" / "middleware.ts"
PROXY = FRONTEND / "proxy.ts"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for path in [MIDDLEWARE, SRC_MIDDLEWARE]:
    if path.exists():
        backup = BACKUP_DIR / f"{path.name}_before_proxy_replacement_{timestamp}.ts"
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

content = '''import { NextRequest, NextResponse } from "next/server";

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isAdminPath = pathname === "/admin" || pathname.startsWith("/admin/");
  const isClientPath = pathname === "/client" || pathname.startsWith("/client/");

  if (!isAdminPath && !isClientPath) {
    return NextResponse.next();
  }

  const expectedOwnerCode = process.env.PORTAL_ACCESS_CODE;
  const ownerAccess = request.cookies.get("portal_access")?.value;
  const clientSession = request.cookies.get("client_session")?.value;

  if (isAdminPath) {
    if (!expectedOwnerCode) {
      return new NextResponse("Admin access is not configured.", { status: 503 });
    }

    if (ownerAccess !== expectedOwnerCode) {
      const loginUrl = new URL("/admin-login", request.url);
      loginUrl.searchParams.set("next", pathname);
      return NextResponse.redirect(loginUrl);
    }

    return NextResponse.next();
  }

  if (isClientPath) {
    if (!clientSession) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("next", pathname);
      return NextResponse.redirect(loginUrl);
    }

    return NextResponse.next();
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*", "/client/:path*"],
};
'''

PROXY.write_text(content, encoding="utf-8")

# Remove deprecated middleware files after backup.
if MIDDLEWARE.exists():
    MIDDLEWARE.unlink()

if SRC_MIDDLEWARE.exists():
    SRC_MIDDLEWARE.unlink()

TEST = ROOT / "test_frontend_proxy_replacement.py"
TEST.write_text(r'''
from pathlib import Path

proxy = Path("frontend/proxy.ts")
middleware_root = Path("frontend/middleware.ts")
middleware_src = Path("frontend/src/middleware.ts")

text = proxy.read_text(encoding="utf-8") if proxy.exists() else ""

print("FRONTEND_PROXY_REPLACEMENT_RESULTS")
print("proxy_exists", proxy.exists())
print("root_middleware_removed", not middleware_root.exists())
print("src_middleware_removed", not middleware_src.exists())
print("exports_proxy", "export function proxy" in text)
print("exports_config", "export const config" in text)
print("admin_matcher", '"/admin/:path*"' in text)
print("client_matcher", '"/client/:path*"' in text)

assert proxy.exists()
assert not middleware_root.exists()
assert not middleware_src.exists()
assert "export function proxy" in text
assert "export const config" in text
assert '"/admin/:path*"' in text
assert '"/client/:path*"' in text

print("FRONTEND_PROXY_REPLACEMENT_OK")
'''.lstrip(), encoding="utf-8")

print("FRONTEND_PROXY_REPLACEMENT_INSTALLED")
print(f"Created: {PROXY}")
print(f"Created: {TEST}")