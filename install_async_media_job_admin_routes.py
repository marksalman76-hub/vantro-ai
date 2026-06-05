from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
BACKUP = ROOT / "backups" / f"async_media_job_admin_routes_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)

MAIN = ROOT / "backend/app/main.py"
FRONTEND_DIR = ROOT / "frontend/src/app/api"

shutil.copy2(MAIN, BACKUP / "main.py")

main_text = MAIN.read_text(encoding="utf-8")

route_block = r'''

@app.get("/admin/media-jobs")
def admin_list_media_jobs():
    from backend.app.runtime.async_media_job_foundation import list_media_jobs
    return list_media_jobs(limit=100)


@app.post("/admin/media-jobs/run-next")
def admin_run_next_media_job():
    from backend.app.runtime.async_media_job_foundation import run_next_media_job
    return run_next_media_job()
'''

if "/admin/media-jobs/run-next" not in main_text:
    MAIN.write_text(main_text.rstrip() + route_block + "\n", encoding="utf-8", newline="\n")

def write_route(path: Path, body: str):
    path.mkdir(parents=True, exist_ok=True)
    (path / "route.ts").write_text(body, encoding="utf-8", newline="\n")

proxy_common = r'''
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_BASE_URL =
  process.env.BACKEND_BASE_URL ||
  process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_TOKEN ||
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";
'''

write_route(
    FRONTEND_DIR / "admin-media-jobs",
    proxy_common + r'''
export async function GET() {
  const headers: Record<string, string> = { "Cache-Control": "no-store" };
  if (ADMIN_TOKEN) {
    headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
    headers["x-admin-token"] = ADMIN_TOKEN;
    headers["x-actor-role"] = "owner_admin";
  }

  const response = await fetch(`${BACKEND_BASE_URL}/admin/media-jobs`, {
    method: "GET",
    cache: "no-store",
    headers,
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status, headers: { "Cache-Control": "no-store" } });
}
'''
)

write_route(
    FRONTEND_DIR / "admin-media-jobs-run-next",
    proxy_common + r'''
export async function POST() {
  const headers: Record<string, string> = { "Cache-Control": "no-store" };
  if (ADMIN_TOKEN) {
    headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
    headers["x-admin-token"] = ADMIN_TOKEN;
    headers["x-actor-role"] = "owner_admin";
  }

  const response = await fetch(`${BACKEND_BASE_URL}/admin/media-jobs/run-next`, {
    method: "POST",
    cache: "no-store",
    headers,
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status, headers: { "Cache-Control": "no-store" } });
}
'''
)

print("ASYNC_MEDIA_JOB_ADMIN_ROUTES_INSTALLED")
print(f"Backup: {BACKUP}")