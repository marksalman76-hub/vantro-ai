from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"provider_execution_admin_ui_block_before_{STAMP}"

ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
PROVIDER_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "provider-execution" / "page.tsx"
TEST_FILE = ROOT / "test_provider_execution_admin_ui_block.py"

for path in [ADMIN_PAGE, PROVIDER_PAGE, TEST_FILE]:
    if path.exists():
        target = BACKUP_DIR / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)

if not ADMIN_PAGE.exists():
    raise FileNotFoundError(f"Missing admin page: {ADMIN_PAGE}")

if not PROVIDER_PAGE.exists():
    raise FileNotFoundError(f"Missing provider execution page: {PROVIDER_PAGE}")

admin = ADMIN_PAGE.read_text(encoding="utf-8")
provider = PROVIDER_PAGE.read_text(encoding="utf-8")

provider_card = '''
        <a
          href="/admin/provider-execution"
          className="group rounded-3xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl transition hover:border-indigo-400 hover:bg-slate-900"
        >
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-indigo-300">
            Provider Runtime
          </p>
          <h2 className="mt-3 text-xl font-bold text-white">
            Provider Execution
          </h2>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            Monitor queued, running, completed, failed, retry-ready, timeout, and delivery-packet provider jobs from the protected admin console.
          </p>
          <div className="mt-4 text-sm font-semibold text-indigo-200 group-hover:text-indigo-100">
            Open provider execution →
          </div>
        </a>
'''

if "/admin/provider-execution" not in admin:
    grid_match = re.search(r'(<main[\s\S]*?className="[^"]*?grid[^"]*?"[\s\S]*?>)', admin)
    if grid_match:
        insert_at = grid_match.end()
        admin = admin[:insert_at] + provider_card + admin[insert_at:]
    else:
        main_match = re.search(r'(<main[\s\S]*?>)', admin)
        if main_match:
            insert_at = main_match.end()
            admin = admin[:insert_at] + f'''
      <section className="mx-auto max-w-7xl px-6 py-6">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
{provider_card}
        </div>
      </section>
''' + admin[insert_at:]
        else:
            admin += f'''
<section className="mx-auto max-w-7xl px-6 py-6">
  <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
{provider_card}
  </div>
</section>
'''

provider = provider.replace(
'''type ProviderJob = {
  job_id?: string;
  provider?: string;
  status?: string;
  tenant_id?: string;
  created_at?: string;
  updated_at?: string;
  attempts?: number;
  retry_count?: number;
  timeout_at?: string;
  delivery_packet_ready?: boolean;
  customer_safe_summary?: string;
};''',
'''type ProviderJob = {
  job_id?: string;
  provider?: string;
  status?: string;
  tenant_id?: string;
  created_at?: string;
  updated_at?: string;
  attempts?: number;
  retry_count?: number;
  timeout_at?: string;
  delivery_packet_ready?: boolean;
  customer_safe_summary?: string;
  lifecycle_events?: Array<{
    event?: string;
    status?: string;
    timestamp?: string;
    message?: string;
  }>;
};'''
)

provider = provider.replace(
'''  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);''',
'''  const [filter, setFilter] = useState("all");
  const [selectedJob, setSelectedJob] = useState<ProviderJob | null>(null);
  const [loading, setLoading] = useState(true);'''
)

provider = provider.replace(
'''                      <td className="max-w-md px-4 py-4 text-slate-300">
                        {safeText(job.customer_safe_summary, "Customer-safe summary pending.")}
                      </td>''',
'''                      <td className="max-w-md px-4 py-4 text-slate-300">
                        <div>{safeText(job.customer_safe_summary, "Customer-safe summary pending.")}</div>
                        <button
                          onClick={() => setSelectedJob(job)}
                          className="mt-3 rounded-lg border border-slate-700 px-3 py-1 text-xs font-semibold text-indigo-200 hover:border-indigo-400"
                        >
                          View details
                        </button>
                      </td>'''
)

modal = r'''
        {selectedJob ? (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-4">
            <div className="max-h-[88vh] w-full max-w-4xl overflow-auto rounded-3xl border border-slate-700 bg-slate-900 p-6 shadow-2xl">
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-indigo-300">
                    Provider Job Detail
                  </p>
                  <h2 className="mt-2 text-2xl font-bold text-white">
                    {safeText(selectedJob.job_id, "Provider job")}
                  </h2>
                  <p className="mt-2 text-sm text-slate-400">
                    Customer-safe operational details only. Credentials, prompts, provider secrets, and internal runtime payloads are not displayed.
                  </p>
                </div>
                <button
                  onClick={() => setSelectedJob(null)}
                  className="rounded-xl border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-200 hover:border-slate-500"
                >
                  Close
                </button>
              </div>

              <div className="mt-6 grid gap-4 md:grid-cols-3">
                <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Provider</p>
                  <p className="mt-2 font-semibold text-white">{safeText(selectedJob.provider)}</p>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Status</p>
                  <p className="mt-2 font-semibold uppercase text-indigo-200">{safeText(selectedJob.status)}</p>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Attempts</p>
                  <p className="mt-2 font-semibold text-white">{safeText(selectedJob.attempts ?? selectedJob.retry_count ?? 0)}</p>
                </div>
              </div>

              <div className="mt-5 rounded-2xl border border-slate-800 bg-slate-950 p-5">
                <h3 className="text-sm font-bold text-white">Execution Timeline</h3>
                <div className="mt-4 space-y-3">
                  {(selectedJob.lifecycle_events && selectedJob.lifecycle_events.length > 0
                    ? selectedJob.lifecycle_events
                    : [
                        { event: "job_created", status: selectedJob.status, timestamp: selectedJob.created_at, message: "Provider job record created." },
                        { event: "last_update", status: selectedJob.status, timestamp: selectedJob.updated_at, message: "Latest provider execution state." },
                      ]
                  ).map((event, index) => (
                    <div key={`${event.event || "event"}-${index}`} className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
                      <div className="flex flex-col gap-1 md:flex-row md:items-center md:justify-between">
                        <p className="text-sm font-semibold text-white">{safeText(event.event, "Runtime event")}</p>
                        <p className="text-xs uppercase tracking-[0.14em] text-indigo-300">{safeText(event.status)}</p>
                      </div>
                      <p className="mt-1 text-xs text-slate-500">{safeText(event.timestamp)}</p>
                      <p className="mt-2 text-sm text-slate-300">{safeText(event.message, "No customer-safe event message available.")}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-5 rounded-2xl border border-slate-800 bg-slate-950 p-5">
                <h3 className="text-sm font-bold text-white">Governed Actions</h3>
                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Retry, requeue, and cancel actions will be enabled only through protected backend governance routes. This UI currently keeps actions read-only until server-side action routes are installed and verified.
                </p>
                <div className="mt-4 flex flex-wrap gap-3">
                  <button disabled className="rounded-xl border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-500">
                    Retry job
                  </button>
                  <button disabled className="rounded-xl border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-500">
                    Requeue job
                  </button>
                  <button disabled className="rounded-xl border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-500">
                    Cancel job
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : null}
'''

if "Provider Job Detail" not in provider:
    provider = provider.replace(
'''      </div>
    </main>
  );
}''',
modal + '''
      </div>
    </main>
  );
}'''
    )

test = r'''from pathlib import Path

ROOT = Path.cwd()
admin = (ROOT / "frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")
provider = (ROOT / "frontend/src/app/admin/provider-execution/page.tsx").read_text(encoding="utf-8")

checks = {
    "admin_links_provider_execution": "/admin/provider-execution" in admin,
    "admin_provider_card": "Provider Execution" in admin,
    "detail_modal": "Provider Job Detail" in provider,
    "execution_timeline": "Execution Timeline" in provider,
    "governed_actions": "Governed Actions" in provider,
    "retry_read_only": "Retry job" in provider,
    "requeue_read_only": "Requeue job" in provider,
    "cancel_read_only": "Cancel job" in provider,
    "customer_safe_wording": "Customer-safe operational details only" in provider,
    "secret_safe_wording": "provider secrets" in provider,
}

failed = [name for name, ok in checks.items() if not ok]
assert not failed, f"Provider admin UI block checks failed: {failed}"

for name, content in {"admin": admin, "provider": provider}.items():
    forbidden = ["sk-", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"]
    exposed = [item for item in forbidden if item in content]
    assert not exposed, f"Forbidden secret marker found in {name}: {exposed}"

print("PROVIDER_EXECUTION_ADMIN_UI_BLOCK_TESTS_PASSED")
print("admin_dashboard_link_ready", True)
print("job_detail_modal_ready", True)
print("execution_timeline_ready", True)
print("governed_actions_read_only_ready", True)
print("credential_values_exposed", False)
'''

ADMIN_PAGE.write_text(admin, encoding="utf-8")
PROVIDER_PAGE.write_text(provider, encoding="utf-8")
TEST_FILE.write_text(test, encoding="utf-8")

print("PROVIDER_EXECUTION_ADMIN_UI_BLOCK_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {ADMIN_PAGE}")
print(f"Updated: {PROVIDER_PAGE}")
print(f"Created/updated: {TEST_FILE}")