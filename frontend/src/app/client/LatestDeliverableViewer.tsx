"use client";

import { useEffect, useMemo, useState } from "react";

type LatestDeliverablePayload = {
  success?: boolean;
  has_real_output?: boolean;
  client_output_truth_checked?: boolean;
  status?: string;
  display_status?: string;
  client_safe_status?: string;
  workflow_status?: string;
  execution_status?: string;
  output_truth_reason?: string;
  title?: string;
  output?: unknown;
  deliverable?: unknown;
  latest_deliverable?: unknown;
  generated_output?: unknown;
  final_output?: unknown;
  asset?: Record<string, unknown>;
  assets?: unknown;
  result?: Record<string, unknown>;
  data?: Record<string, unknown>;
};

function readable(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return value.trim();
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return "";
  }
}

function firstMeaningful(...values: unknown[]): string {
  for (const value of values) {
    const text = readable(value);
    if (!text) continue;
    const lower = text.toLowerCase();
    if (["completed", "complete", "success", "successful", "done", "pending", "null", "undefined"].includes(lower)) continue;
    return text;
  }
  return "";
}

function pickAssetUrl(payload: LatestDeliverablePayload): string {
  const asset: Record<string, unknown> = (payload.asset || payload.result?.asset || payload.data?.asset || {}) as Record<string, unknown>;
  const keys = ["signed_preview_url", "preview_url", "signed_download_url", "download_url", "public_url", "url"];
  for (const key of keys) {
    const value = asset[key];
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  return "";
}

export default function LatestDeliverableViewer() {
  const [payload, setPayload] = useState<LatestDeliverablePayload | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function loadLatestDeliverable() {
      try {
        const res = await fetch("/api/client-latest-deliverable", {
          method: "GET",
          cache: "no-store",
          credentials: "include",
        });
        const json = await res.json();
        if (active) setPayload(json);
      } catch {
        if (active) {
          setPayload({
            success: false,
            has_real_output: false,
            client_safe_status: "Output pending",
            output_truth_reason: "Latest deliverable is not available yet.",
          });
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    loadLatestDeliverable();
    return () => {
      active = false;
    };
  }, []);

  const outputText = useMemo(() => {
    if (!payload) return "";
    return firstMeaningful(
      payload.latest_deliverable,
      payload.deliverable,
      payload.generated_output,
      payload.final_output,
      payload.output,
      payload.result?.latest_deliverable,
      payload.result?.deliverable,
      payload.result?.generated_output,
      payload.result?.final_output,
      payload.result?.output,
      payload.data?.latest_deliverable,
      payload.data?.deliverable,
      payload.data?.generated_output,
      payload.data?.final_output,
      payload.data?.output
    );
  }, [payload]);

  const assetUrl = useMemo(() => (payload ? pickAssetUrl(payload) : ""), [payload]);
  const hasRealOutput = Boolean(payload?.has_real_output && (outputText || assetUrl));
  const status = loading
    ? "Checking latest output"
    : hasRealOutput
      ? "Completed"
      : payload?.client_safe_status || payload?.display_status || "Output pending";

  return (
    <section className="mt-6 rounded-2xl border border-indigo-400/20 bg-slate-950/70 p-5 shadow-lg shadow-indigo-950/20">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-indigo-300">
            Latest deliverable
          </p>
          <h2 className="mt-1 text-lg font-semibold text-white">
            Client output viewer
          </h2>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
          hasRealOutput
            ? "bg-emerald-400/10 text-emerald-300 ring-1 ring-emerald-300/30"
            : "bg-amber-400/10 text-amber-300 ring-1 ring-amber-300/30"
        }`}>
          {status}
        </span>
      </div>

      {loading ? (
        <p className="text-sm text-slate-300">Checking for the latest real deliverable...</p>
      ) : hasRealOutput ? (
        <div className="space-y-4">
          {outputText ? (
            <pre className="max-h-80 overflow-auto whitespace-pre-wrap rounded-xl border border-slate-700/70 bg-black/30 p-4 text-sm leading-6 text-slate-100">
              {outputText}
            </pre>
          ) : null}

          {assetUrl ? (
            <div className="flex flex-wrap gap-3">
              <a
                href={assetUrl}
                target="_blank"
                rel="noreferrer"
                className="rounded-xl bg-indigo-500 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-400"
              >
                Preview latest asset
              </a>
              <a
                href={assetUrl}
                download
                className="rounded-xl border border-indigo-300/30 px-4 py-2 text-sm font-semibold text-indigo-100 hover:bg-indigo-400/10"
              >
                Download
              </a>
            </div>
          ) : null}
        </div>
      ) : (
        <div className="rounded-xl border border-amber-300/20 bg-amber-300/5 p-4 text-sm text-amber-100">
          {payload?.output_truth_reason || "No real deliverable, output, or generated asset exists yet."}
        </div>
      )}
    </section>
  );
}
