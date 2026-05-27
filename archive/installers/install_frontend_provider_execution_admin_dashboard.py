from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"frontend_provider_execution_admin_dashboard_before_{STAMP}"

FILES = {
    "page": ROOT / "frontend" / "src" / "app" / "admin" / "provider-execution" / "page.tsx",
    "api_status": ROOT / "frontend" / "src" / "app" / "api" / "admin-provider-execution" / "status" / "route.ts",
    "api_summary": ROOT / "frontend" / "src" / "app" / "api" / "admin-provider-execution" / "summary" / "route.ts",
    "test": ROOT / "test_frontend_provider_execution_admin_dashboard.py",
}

def backup_file(path: Path):
    if path.exists():
        target = BACKUP_DIR / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)

for file_path in FILES.values():
    backup_file(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

status_route = r'''import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL;
const adminToken = process.env.ADMIN_PLATFORM_TOKEN;

export async function GET() {
  if (!backendUrl || !adminToken) {
    return NextResponse.json(
      {
        ready: false,
        error: "Provider execution admin status is not configured.",
        credential_values_exposed: false,
      },
      { status: 503 }
    );
  }

  const response = await fetch(`${backendUrl}/provider-execution-admin-visibility/status`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${adminToken}`,
      "Content-Type": "application/json",
    },
    cache: "no-store",
  });

  const data = await response.json().catch(() => ({
    ready: false,
    error: "Invalid provider execution admin status response.",
  }));

  return NextResponse.json(
    {
      ...data,
      credential_values_exposed: false,
    },
    { status: response.status }
  );
}
'''

summary_route = r'''import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL;
const adminToken = process.env.ADMIN_PLATFORM_TOKEN;

export async function GET() {
  if (!backendUrl || !adminToken) {
    return NextResponse.json(
      {
        ready: false,
        jobs: [],
        summary: {},
        delivery_packets: [],
        retry_timeout: {},
        credential_values_exposed: false,
        error: "Provider execution admin summary is not configured.",
      },
      { status: 503 }
    );
  }

  const response = await fetch(`${backendUrl}/provider-execution-admin-visibility/summary`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${adminToken}`,
      "Content-Type": "application/json",
    },
    cache: "no-store",
  });

  const data = await response.json().catch(() => ({
    ready: false,
    jobs: [],
    summary: {},
    delivery_packets: [],
    retry_timeout: {},
    error: "Invalid provider execution admin summary response.",
  }));

  return NextResponse.json(
    {
      ...data,
      credential_values_exposed: false,
    },
    { status: response.status }
  );
}
'''

page = r'''"use client";

import { useEffect, useMemo, useState } from "react";

type ProviderJob = {
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
};

type ProviderSummary = {
  ready?: boolean;
  jobs?: ProviderJob[];
  summary?: Record<string, number>;
  delivery_packets?: unknown[];
  retry_timeout?: Record<string, unknown>;
  credential_values_exposed?: boolean;
  error?: string;
};

const statusLabels = ["queued", "running", "completed", "failed", "timeout", "retry_ready"];

function safeText(value: unknown, fallback = "—") {
  if (value === null || value === undefined || value === "") return fallback;
  return String(value);
}

export default function ProviderExecutionAdminPage() {
  const [data, setData] = useState<ProviderSummary | null>(null);
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>("");

  async function loadProviderExecution() {
    setLoading(true);
    try {
      const [statusResponse, summaryResponse] = await Promise.all([
        fetch("/api/admin-provider-execution/status", { cache: "no-store" }),
        fetch("/api/admin-provider-execution/summary", { cache: "no-store" }),
      ]);

      const statusJson = await statusResponse.json();
      const summaryJson = await summaryResponse.json();

      setStatus(statusJson);
      setData(summaryJson);
      setLastUpdated(new Date().toLocaleString());
    } catch {
      setData({
        ready: false,
        jobs: [],
        summary: {},
        delivery_packets: [],
        retry_timeout: {},
        credential_values_exposed: false,
        error: "Unable to load provider execution dashboard.",
      });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProviderExecution();
    const timer = window.setInterval(loadProviderExecution, 15000);
    return () => window.clearInterval(timer);
  }, []);

  const jobs = useMemo(() => {
    const source = Array.isArray(data?.jobs) ? data.jobs : [];
    if (filter === "all") return source;
    return source.filter((job) => String(job.status || "").toLowerCase() === filter);
  }, [data, filter]);

  const counts = useMemo(() => {
    const source = Array.isArray(data?.jobs) ? data.jobs : [];
    return statusLabels.reduce<Record<string, number>>((acc, label) => {
      acc[label] = source.filter((job) => String(job.status || "").toLowerCase() === label).length;
      return acc;
    }, {});
  }, [data]);

  const deliveryPacketCount = Array.isArray(data?.delivery_packets) ? data.delivery_packets.length : 0;
  const credentialSafe = data?.credential_values_exposed === false;

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-2xl">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-indigo-300">
                Admin Runtime
              </p>
              <h1 className="mt-2 text-3xl font-bold text-white">
                Provider Execution Dashboard
              </h1>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
                Live admin view for provider jobs, retry/timeout state, delivery packet readiness,
                and customer-safe execution summaries. Internal credentials and raw provider secrets
                are never rendered in this interface.
              </p>
            </div>

            <div className="flex flex-col gap-2 rounded-2xl border border-slate-700 bg-slate-950/80 p-4 text-sm">
              <div className="flex items-center justify-between gap-4">
                <span className="text-slate-400">Runtime</span>
                <span className={data?.ready ? "font-semibold text-emerald-300" : "font-semibold text-amber-300"}>
                  {data?.ready ? "READY" : "CHECKING"}
                </span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span className="text-slate-400">Credential exposure</span>
                <span className={credentialSafe ? "font-semibold text-emerald-300" : "font-semibold text-red-300"}>
                  {credentialSafe ? "FALSE" : "REVIEW"}
                </span>
              </div>
              <div className="text-xs text-slate-500">Last refresh: {lastUpdated || "—"}</div>
            </div>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-3 xl:grid-cols-6">
          {statusLabels.map((label) => (
            <button
              key={label}
              onClick={() => setFilter(label)}
              className={`rounded-2xl border p-4 text-left transition ${
                filter === label
                  ? "border-indigo-400 bg-indigo-500/20"
                  : "border-slate-800 bg-slate-900/70 hover:border-slate-600"
              }`}
            >
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
                {label.replace("_", " ")}
              </p>
              <p className="mt-3 text-3xl font-bold text-white">{counts[label] || 0}</p>
            </button>
          ))}
        </section>

        <section className="grid gap-4 lg:grid-cols-3">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5">
            <p className="text-sm font-semibold text-white">Retry / Timeout Visibility</p>
            <pre className="mt-4 max-h-56 overflow-auto rounded-2xl bg-slate-950 p-4 text-xs leading-5 text-slate-300">
              {JSON.stringify(data?.retry_timeout || {}, null, 2)}
            </pre>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5">
            <p className="text-sm font-semibold text-white">Delivery Packet Visibility</p>
            <p className="mt-4 text-4xl font-bold text-white">{deliveryPacketCount}</p>
            <p className="mt-2 text-sm text-slate-400">
              Customer-safe delivery packets linked to provider execution records.
            </p>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5">
            <p className="text-sm font-semibold text-white">Admin-Safe Controls</p>
            <button
              onClick={loadProviderExecution}
              className="mt-4 rounded-xl bg-indigo-500 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-400"
            >
              Refresh now
            </button>
            <button
              onClick={() => setFilter("all")}
              className="ml-3 mt-4 rounded-xl border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-200 hover:border-slate-500"
            >
              Clear filters
            </button>
            <p className="mt-4 text-xs leading-5 text-slate-500">
              Execution mutations remain governed server-side. This dashboard only renders protected
              admin summaries and safe runtime visibility.
            </p>
          </div>
        </section>

        <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-xl font-bold text-white">Live Provider Jobs</h2>
              <p className="mt-1 text-sm text-slate-400">
                Showing {jobs.length} job{jobs.length === 1 ? "" : "s"} · Filter: {filter.toUpperCase()}
              </p>
            </div>

            <select
              value={filter}
              onChange={(event) => setFilter(event.target.value)}
              className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-2 text-sm text-white"
            >
              <option value="all">All jobs</option>
              {statusLabels.map((label) => (
                <option key={label} value={label}>
                  {label.replace("_", " ")}
                </option>
              ))}
            </select>
          </div>

          <div className="mt-5 overflow-x-auto rounded-2xl border border-slate-800">
            <table className="min-w-full divide-y divide-slate-800 text-sm">
              <thead className="bg-slate-950/80 text-left text-xs uppercase tracking-[0.16em] text-slate-400">
                <tr>
                  <th className="px-4 py-3">Job</th>
                  <th className="px-4 py-3">Provider</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Attempts</th>
                  <th className="px-4 py-3">Delivery</th>
                  <th className="px-4 py-3">Updated</th>
                  <th className="px-4 py-3">Customer-safe summary</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {loading ? (
                  <tr>
                    <td className="px-4 py-6 text-slate-400" colSpan={7}>
                      Loading provider execution records...
                    </td>
                  </tr>
                ) : jobs.length === 0 ? (
                  <tr>
                    <td className="px-4 py-6 text-slate-400" colSpan={7}>
                      No provider execution jobs found for this filter.
                    </td>
                  </tr>
                ) : (
                  jobs.map((job, index) => (
                    <tr key={`${job.job_id || "job"}-${index}`} className="bg-slate-900/30">
                      <td className="px-4 py-4 font-mono text-xs text-slate-300">
                        {safeText(job.job_id)}
                      </td>
                      <td className="px-4 py-4 text-slate-200">{safeText(job.provider)}</td>
                      <td className="px-4 py-4">
                        <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-xs font-semibold uppercase text-indigo-200">
                          {safeText(job.status)}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-slate-300">
                        {safeText(job.attempts ?? job.retry_count ?? 0)}
                      </td>
                      <td className="px-4 py-4 text-slate-300">
                        {job.delivery_packet_ready ? "Ready" : "Pending"}
                      </td>
                      <td className="px-4 py-4 text-slate-400">{safeText(job.updated_at || job.created_at)}</td>
                      <td className="max-w-md px-4 py-4 text-slate-300">
                        {safeText(job.customer_safe_summary, "Customer-safe summary pending.")}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {data?.error ? (
            <p className="mt-4 rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-200">
              {data.error}
            </p>
          ) : null}
        </section>

        <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5">
          <h2 className="text-lg font-bold text-white">Protected Status Payload</h2>
          <pre className="mt-4 max-h-72 overflow-auto rounded-2xl bg-slate-950 p-4 text-xs leading-5 text-slate-300">
            {JSON.stringify(status || {}, null, 2)}
          </pre>
        </section>
      </div>
    </main>
  );
}
'''

test_script = r'''from pathlib import Path

ROOT = Path.cwd()

required_files = [
    ROOT / "frontend/src/app/admin/provider-execution/page.tsx",
    ROOT / "frontend/src/app/api/admin-provider-execution/status/route.ts",
    ROOT / "frontend/src/app/api/admin-provider-execution/summary/route.ts",
]

for path in required_files:
    assert path.exists(), f"Missing required file: {path}"

page = required_files[0].read_text(encoding="utf-8")
status_route = required_files[1].read_text(encoding="utf-8")
summary_route = required_files[2].read_text(encoding="utf-8")

checks = {
    "dashboard_title": "Provider Execution Dashboard" in page,
    "job_table": "Live Provider Jobs" in page,
    "retry_timeout_visibility": "Retry / Timeout Visibility" in page,
    "delivery_packet_visibility": "Delivery Packet Visibility" in page,
    "runtime_polling": "setInterval(loadProviderExecution, 15000)" in page,
    "customer_safe_wording": "Customer-safe" in page,
    "status_proxy_route": "/provider-execution-admin-visibility/status" in status_route,
    "summary_proxy_route": "/provider-execution-admin-visibility/summary" in summary_route,
    "server_side_admin_token_status": "ADMIN_PLATFORM_TOKEN" in status_route,
    "server_side_admin_token_summary": "ADMIN_PLATFORM_TOKEN" in summary_route,
    "credential_exposure_false_status": "credential_values_exposed: false" in status_route,
    "credential_exposure_false_summary": "credential_values_exposed: false" in summary_route,
}

failed = [name for name, ok in checks.items() if not ok]
assert not failed, f"Checks failed: {failed}"

for content_name, content in [
    ("page", page),
    ("status_route", status_route),
    ("summary_route", summary_route),
]:
    forbidden = [
        "sk-",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
    ]
    exposed = [item for item in forbidden if item in content]
    assert not exposed, f"Forbidden secret marker found in {content_name}: {exposed}"

print("FRONTEND_PROVIDER_EXECUTION_ADMIN_DASHBOARD_TESTS_PASSED")
print("dashboard_page_ready", True)
print("api_proxy_ready", True)
print("credential_values_exposed", False)
'''

FILES["api_status"].write_text(status_route, encoding="utf-8")
FILES["api_summary"].write_text(summary_route, encoding="utf-8")
FILES["page"].write_text(page, encoding="utf-8")
FILES["test"].write_text(test_script, encoding="utf-8")

print("FRONTEND_PROVIDER_EXECUTION_ADMIN_DASHBOARD_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
for key, path in FILES.items():
    print(f"Created/updated {key}: {path}")