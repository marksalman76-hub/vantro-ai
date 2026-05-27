from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "api" / "client-execution-matrix" / "route.ts"

if not target.exists():
    raise SystemExit(f"Missing file: {target}")

backup_dir = root / "backups" / f"row6_raw_proxy_body_sanitizer_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "route.ts")

text = target.read_text(encoding="utf-8")

helper = '''
function sanitizeCustomerSafeBody(body: string): string {
  return body
    .replace(/internal_prompt_exposure_blocked/gi, "request_details_protected")
    .replace(/backend_architecture_exposure_blocked/gi, "system_details_protected")
    .replace(/internal prompt/gi, "request details")
    .replace(/system prompt/gi, "request details")
    .replace(/developer message/gi, "request details")
    .replace(/backend architecture/gi, "system details")
    .replace(/raw json/gi, "details")
    .replace(/debug/gi, "support")
    .replace(/webhook/gi, "connection");
}

'''

if "function sanitizeCustomerSafeBody" not in text:
    marker = "async function proxy(req: NextRequest, path: string) {"
    if marker not in text:
        raise SystemExit("proxy marker not found")
    text = text.replace(marker, helper + marker, 1)

old = "  const body = await res.text();"
new = '''  const rawBody = await res.text();
  const body = sanitizeCustomerSafeBody(rawBody);'''

if old not in text:
    raise SystemExit("raw body read target not found")

text = text.replace(old, new, 1)

target.write_text(text, encoding="utf-8")

print("ROW6_RAW_PROXY_BODY_SANITIZER_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")