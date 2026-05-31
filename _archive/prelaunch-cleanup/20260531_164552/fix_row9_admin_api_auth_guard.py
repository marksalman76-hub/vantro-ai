from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()

targets = [
    root / "frontend" / "src" / "app" / "api" / "admin-runtime" / "route.ts",
    root / "frontend" / "src" / "app" / "api" / "admin-provider-execution" / "summary" / "route.ts",
]

backup_dir = root / "backups" / f"row9_admin_api_auth_guard_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

guard = '''
function isAdminRequest(req: Request): boolean {
  const expected = process.env.ADMIN_PLATFORM_TOKEN || "";
  if (!expected) return false;

  const auth = req.headers.get("authorization") || "";
  const adminHeader = req.headers.get("x-admin-token") || "";

  return auth === `Bearer ${expected}` || adminHeader === expected;
}

function unauthorizedAdminResponse() {
  return NextResponse.json(
    {
      success: false,
      error: "unauthorized",
      message: "Admin access required.",
      credential_values_exposed: false,
      customer_safe: true,
    },
    { status: 401 }
  );
}

'''

changed = []

for target in targets:
    if not target.exists():
        print(f"SKIPPED missing: {target}")
        continue

    shutil.copy2(target, backup_dir / target.name)

    text = target.read_text(encoding="utf-8")

    if "function isAdminRequest" not in text:
        marker = "const BACKEND_URL" if "const BACKEND_URL" in text else "const backendUrl"
        if marker not in text:
            raise SystemExit(f"Could not locate insert marker in {target}")
        text = text.replace(marker, guard + marker, 1)

    text = text.replace("export async function GET() {", "export async function GET(req: Request) {", 1)

    guard_line = '''  if (!isAdminRequest(req)) {
    return unauthorizedAdminResponse();
  }

'''

    if "return unauthorizedAdminResponse();" not in text.split("export async function GET", 1)[-1]:
        marker = "export async function GET(req: Request) {\n"
        if marker not in text:
            raise SystemExit(f"Could not locate GET marker in {target}")
        text = text.replace(marker, marker + guard_line, 1)

    target.write_text(text, encoding="utf-8")
    changed.append(str(target))

print("ROW9_ADMIN_API_AUTH_GUARD_INSTALLED")
print(f"Backup folder: {backup_dir}")
print("Changed:")
for item in changed:
    print(f"- {item}")