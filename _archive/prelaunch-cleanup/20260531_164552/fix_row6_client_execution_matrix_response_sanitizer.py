from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "api" / "client-execution-matrix" / "route.ts"

backup_dir = root / "backups" / f"row6_client_execution_matrix_sanitizer_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

if not target.exists():
    raise SystemExit(f"Missing file: {target}")

shutil.copy2(target, backup_dir / "route.ts")

text = target.read_text(encoding="utf-8")

if "sanitizeCustomerExecutionMatrixPayload" not in text:
    marker = "async function proxy(req: NextRequest, path: string) {"

    sanitizer = '''
function sanitizeCustomerExecutionMatrixPayload(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map((item) => sanitizeCustomerExecutionMatrixPayload(item));
  }

  if (value && typeof value === "object") {
    const output: Record<string, unknown> = {};

    for (const [rawKey, rawValue] of Object.entries(value as Record<string, unknown>)) {
      let safeKey = rawKey
        .replace(/internal_prompt_exposure_blocked/gi, "request_details_protected")
        .replace(/backend_architecture_exposure_blocked/gi, "system_details_protected");

      output[safeKey] = sanitizeCustomerExecutionMatrixPayload(rawValue);
    }

    return output;
  }

  if (typeof value === "string") {
    return value
      .replace(/internal_prompt_exposure_blocked/gi, "request_details_protected")
      .replace(/backend_architecture_exposure_blocked/gi, "system_details_protected")
      .replace(/internal prompt/gi, "request details")
      .replace(/system prompt/gi, "request details")
      .replace(/developer message/gi, "request details")
      .replace(/backend architecture/gi, "system details")
      .replace(/raw json/gi, "details")
      .replace(/debug/gi, "support")
      .replace(/webhook/gi, "connection")
      .replace(/runtime/gi, "system");
  }

  return value;
}

'''

    if marker not in text:
        raise SystemExit("proxy function marker not found.")

    text = text.replace(marker, sanitizer + marker, 1)

old_return = "return NextResponse.json(data, { status: upstream.status });"
new_return = "return NextResponse.json(sanitizeCustomerExecutionMatrixPayload(data), { status: upstream.status });"

if old_return not in text:
    raise SystemExit("Expected NextResponse.json return target not found.")

text = text.replace(old_return, new_return, 1)

target.write_text(text, encoding="utf-8")

print("ROW6_CLIENT_EXECUTION_MATRIX_RESPONSE_SANITIZER_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")