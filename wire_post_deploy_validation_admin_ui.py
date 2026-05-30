from pathlib import Path
from datetime import datetime

page = Path("frontend/src/app/admin/page.tsx")
api_route = Path("frontend/src/app/api/admin-post-deploy-validation-status/route.ts")

backup_dir = Path("backups") / ("post_deploy_validation_admin_ui_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)

for path in [page, api_route]:
    if path.exists():
        (backup_dir / path.name.replace("/", "_")).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

api_route.parent.mkdir(parents=True, exist_ok=True)

api_route.write_text('''import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.trance-formation.com.au";

export async function GET() {
  const token =
    process.env.ADMIN_PLATFORM_TOKEN ||
    process.env.NEXT_PUBLIC_ADMIN_PLATFORM_TOKEN ||
    process.env.ADMIN_AUTH_SECRET ||
    "";

  const response = await fetch(`${API_BASE}/admin/post-deploy-validation/status`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "x-admin-token": token,
      "x-actor-role": "owner_admin",
      "x-tenant-id": "owner_admin",
    },
    cache: "no-store",
  });

  const data = await response.json().catch(() => ({
    success: false,
    error: "invalid_json_response",
  }));

  return NextResponse.json(data, { status: response.status });
}
''', encoding="utf-8")

text = page.read_text(encoding="utf-8")

state_block = '''  const [postDeployValidation, setPostDeployValidation] = useState<any>(null);
'''
if "postDeployValidation" not in text:
    text = text.replace("export default function AdminPage() {", "export default function AdminPage() {\n" + state_block)

effect_block = '''
  useEffect(() => {
    fetch("/api/admin-post-deploy-validation-status", { cache: "no-store" })
      .then((res) => res.json())
      .then((data) => setPostDeployValidation(data))
      .catch(() => setPostDeployValidation({ success: false, error: "post_deploy_validation_status_unavailable" }));
  }, []);
'''
if "admin-post-deploy-validation-status" not in text:
    marker = "  return ("
    text = text.replace(marker, effect_block + "\n" + marker, 1)

panel = '''
        <section className="rounded-2xl border border-slate-800 bg-slate-950/80 p-5 shadow-xl">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-indigo-300">Release readiness</p>
              <h2 className="mt-2 text-xl font-semibold text-white">Post-deploy validation</h2>
              <p className="mt-2 text-sm text-slate-400">
                QA-backed deployment checks, release scoring, and advisory rollback readiness.
              </p>
            </div>
            <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
              postDeployValidation?.success ? "bg-emerald-500/15 text-emerald-300" : "bg-amber-500/15 text-amber-300"
            }`}>
              {postDeployValidation?.success ? "READY" : "CHECK"}
            </span>
          </div>

          <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
              <p className="text-xs text-slate-500">Required checks</p>
              <p className="mt-1 text-2xl font-semibold text-white">{postDeployValidation?.required_check_count ?? "—"}</p>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
              <p className="text-xs text-slate-500">Release scoring</p>
              <p className="mt-1 text-sm font-semibold text-white">{postDeployValidation?.release_readiness_scoring_enabled ? "Enabled" : "Pending"}</p>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
              <p className="text-xs text-slate-500">QA agent</p>
              <p className="mt-1 text-sm font-semibold text-white">{postDeployValidation?.qa_testing_agent_supported ? "Supported" : "Pending"}</p>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
              <p className="text-xs text-slate-500">Credential exposure</p>
              <p className="mt-1 text-sm font-semibold text-white">{postDeployValidation?.credential_values_exposed ? "Review" : "Protected"}</p>
            </div>
          </div>
        </section>
'''

if "Post-deploy validation" not in text:
    text = text.replace("<main", panel + "\n      <main", 1)

page.write_text(text, encoding="utf-8")

print("POST_DEPLOY_VALIDATION_ADMIN_UI_WIRED")
print("Backup:", backup_dir)
print("Updated:", page)
print("Created:", api_route)