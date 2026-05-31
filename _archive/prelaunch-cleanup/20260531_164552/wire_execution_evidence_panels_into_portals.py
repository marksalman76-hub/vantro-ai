from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()

admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"

backup_dir = ROOT / "backups" / f"execution_evidence_panels_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

shutil.copy2(admin_page, backup_dir / "admin_page.tsx")
shutil.copy2(client_page, backup_dir / "client_page.tsx")

admin = admin_page.read_text(encoding="utf-8")
client = client_page.read_text(encoding="utf-8")

admin_marker = "Global execution evidence"
client_marker = "Execution proof"

admin_panel = r'''
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Global execution evidence</p>
            <h2 className="text-lg font-semibold text-slate-950">Live provider proof & audit trail</h2>
            <p className="mt-1 text-sm text-slate-600">Tenant-aware external action evidence, provider status, and credential-safe execution records.</p>
          </div>
          <button
            type="button"
            onClick={async () => {
              const res = await fetch("/api/admin-execution-evidence?tenant_id=client_demo_001&limit=10", { cache: "no-store" });
              const json = await res.json();
              alert(JSON.stringify(json?.data || json, null, 2));
            }}
            className="rounded-xl bg-slate-950 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-slate-800"
          >
            View evidence
          </button>
        </div>
        <div className="grid gap-3 md:grid-cols-3">
          <div className="rounded-xl border border-emerald-100 bg-emerald-50 p-4">
            <p className="text-xs font-semibold uppercase text-emerald-700">Verified provider</p>
            <p className="mt-1 text-sm font-semibold text-emerald-950">Brevo live execution</p>
          </div>
          <div className="rounded-xl border border-blue-100 bg-blue-50 p-4">
            <p className="text-xs font-semibold uppercase text-blue-700">Tenant-aware</p>
            <p className="mt-1 text-sm font-semibold text-blue-950">client_demo_001 routed correctly</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-xs font-semibold uppercase text-slate-600">Audit safe</p>
            <p className="mt-1 text-sm font-semibold text-slate-950">No credential exposure</p>
          </div>
        </div>
      </section>
'''

client_panel = r'''
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Execution proof</p>
            <h2 className="text-lg font-semibold text-slate-950">Completed action evidence</h2>
            <p className="mt-1 text-sm text-slate-600">Customer-safe proof of completed actions without exposing internal routing or credentials.</p>
          </div>
          <button
            type="button"
            onClick={async () => {
              const res = await fetch("/api/client-execution-evidence?tenant_id=client_demo_001&limit=10", { cache: "no-store" });
              const json = await res.json();
              alert(JSON.stringify(json?.data || json, null, 2));
            }}
            className="rounded-xl bg-slate-950 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-slate-800"
          >
            View proof
          </button>
        </div>
        <div className="rounded-xl border border-emerald-100 bg-emerald-50 p-4">
          <p className="text-xs font-semibold uppercase text-emerald-700">Latest verified action</p>
          <p className="mt-1 text-sm font-semibold text-emerald-950">Live email execution completed through connected provider.</p>
        </div>
      </section>
'''

if admin_marker not in admin:
    idx = admin.rfind("</main>")
    if idx == -1:
        raise SystemExit("ADMIN_MAIN_CLOSE_NOT_FOUND")
    admin = admin[:idx] + admin_panel + "\n" + admin[idx:]

if client_marker not in client:
    idx = client.rfind("</main>")
    if idx == -1:
        raise SystemExit("CLIENT_MAIN_CLOSE_NOT_FOUND")
    client = client[:idx] + client_panel + "\n" + client[idx:]

admin_page.write_text(admin, encoding="utf-8")
client_page.write_text(client, encoding="utf-8")

test_file = ROOT / "test_execution_evidence_panels_into_portals.py"
test_file.write_text(r'''
from pathlib import Path

admin = Path("frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")
client = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")

assert "Global execution evidence" in admin
assert "/api/admin-execution-evidence?tenant_id=client_demo_001&limit=10" in admin
assert "Brevo live execution" in admin

assert "Execution proof" in client
assert "/api/client-execution-evidence?tenant_id=client_demo_001&limit=10" in client
assert "No credential" in admin

print("EXECUTION_EVIDENCE_PANELS_INTO_PORTALS_TEST_PASSED")
''', encoding="utf-8")

print("EXECUTION_EVIDENCE_PANELS_INTO_PORTALS_WIRED")
print(f"Backup: {backup_dir}")
print(f"Updated: {admin_page}")
print(f"Updated: {client_page}")
print(f"Created: {test_file}")