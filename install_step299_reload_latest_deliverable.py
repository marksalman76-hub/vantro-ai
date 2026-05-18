from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
API_DIR = ROOT / "frontend" / "src" / "app" / "api" / "client-latest-deliverable"
API_FILE = API_DIR / "route.ts"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(exist_ok=True)
API_DIR.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

text = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_step299_reload_latest_deliverable_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

old_effect = '''  useEffect(() => {
    fetch("/api/client-me")
      .then((r) => r.json())
      .then((data) => setAccount(data?.account || data))
      .catch(() => {});
  }, []);'''

new_effect = '''  useEffect(() => {
    fetch("/api/client-me")
      .then((r) => r.json())
      .then((data) => setAccount(data?.account || data))
      .catch(() => {});

    fetch("/api/client-latest-deliverable", {
      method: "GET",
      credentials: "include",
    })
      .then((r) => r.json())
      .then((data) => {
        if (data?.success && data?.deliverable) {
          setLiveDeliverable(data.deliverable);
          setExecutionState("completed");
          setReviewStatus("pending");
        }
      })
      .catch(() => {});
  }, []);'''

if old_effect not in text:
    raise SystemExit("ERROR: useEffect block not found.")

text = text.replace(old_effect, new_effect)

PAGE.write_text(text, encoding="utf-8")

API_FILE.write_text('''import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import path from "path";

const DATA_FILE = path.join(process.cwd(), ".runtime-data", "client-executions.json");

export async function GET() {
  try {
    const raw = await readFile(DATA_FILE, "utf-8");
    const executions = JSON.parse(raw);

    if (!Array.isArray(executions) || executions.length === 0) {
      return NextResponse.json({
        success: true,
        deliverable: null,
      });
    }

    const latest = executions[0];

    return NextResponse.json({
      success: true,
      execution: latest,
      deliverable: latest?.deliverable || null,
    });
  } catch {
    return NextResponse.json({
      success: true,
      deliverable: null,
    });
  }
}
''', encoding="utf-8")

print("STEP_299_RELOAD_LATEST_DELIVERABLE_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {API_FILE}")
print("STEP_299_OK")