"use client";

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
  lifecycle_events?: Array<{
    event?: string;
    status?: string;
    timestamp?: string;
    message?: string;
  }>;
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
  const [selectedJob, setSelectedJob] = useState<ProviderJob | null>(null);
  const [actionMessage, setActionMessage] = useState<string>("");
  const [actionBusy, setActionBusy] = useState<string>("");
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

  async function runGovernedAction(action: "retry" | "requeue" | "cancel") {
    if (!selectedJob?.job_id) {
      setActionMessage("No provider job selected.");
      return;
    }

    setActionBusy(action);
    setActionMessage("");

    try {
      const response = await fetch(`/api/admin-provider-execution/${action}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_id: selectedJob.job_id,
          reason: `Admin requested governed provider ${action}.`,
        }),
      });

      const result = await response.json();

      if (!response.ok || result?.credential_values_exposed !== false) {
        setActionMessage(result?.error || `Provider ${action} request was not accepted.`);
        return;
      }

      setActionMessage(result?.message || `Governed provider ${action} request accepted.`);
      await loadProviderExecution();
    } catch {
      setActionMessage(`Provider ${action} request failed before reaching the governed runtime.`);
    } finally {
      setActionBusy("");
    }
  }

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
                        <div>{safeText(job.customer_safe_summary, "Customer-safe summary pending.")}</div>
                        <button
                          onClick={() => setSelectedJob(job)}
                          className="mt-3 rounded-lg border border-slate-700 px-3 py-1 text-xs font-semibold text-indigo-200 hover:border-indigo-400"
                        >
                          View details
                        </button>
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
                  Retry, requeue, and cancel actions are routed through protected backend governance routes. Actions are accepted only as admin-governed runtime requests and do not expose internal credentials or provider payloads.
                </p>
                <div className="mt-4 flex flex-wrap gap-3">
                  <button
                    onClick={() => runGovernedAction("retry")}
                    disabled={Boolean(actionBusy)}
                    className="rounded-xl border border-emerald-500/50 px-4 py-2 text-sm font-semibold text-emerald-200 hover:border-emerald-300 disabled:opacity-50"
                  >
                    {actionBusy === "retry" ? "Requesting..." : "Retry job"}
                  </button>
                  <button
                    onClick={() => runGovernedAction("requeue")}
                    disabled={Boolean(actionBusy)}
                    className="rounded-xl border border-indigo-500/50 px-4 py-2 text-sm font-semibold text-indigo-200 hover:border-indigo-300 disabled:opacity-50"
                  >
                    {actionBusy === "requeue" ? "Requesting..." : "Requeue job"}
                  </button>
                  <button
                    onClick={() => runGovernedAction("cancel")}
                    disabled={Boolean(actionBusy)}
                    className="rounded-xl border border-amber-500/50 px-4 py-2 text-sm font-semibold text-amber-200 hover:border-amber-300 disabled:opacity-50"
                  >
                    {actionBusy === "cancel" ? "Requesting..." : "Cancel job"}
                  </button>
                </div>
                {actionMessage ? (
                  <p className="mt-4 rounded-xl border border-slate-700 bg-slate-900 p-3 text-sm text-slate-200">
                    {actionMessage}
                  </p>
                ) : null}
              </div>
            </div>
          </div>
        ) : null}

      </div>
    </main>
  );
}
