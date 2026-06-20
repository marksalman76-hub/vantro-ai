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
  media_job_id?: string;
  final_deliverable_ready?: boolean;
  final_deliverable_status?: string;
  final_deliverable_type?: string;
  final_deliverable_reason?: string;
  final_deliverable_asset_ids?: unknown;
  final_deliverable_asset_count?: number;
  final_combined_asset_status?: string;
  client_ready_delivery?: boolean;
  client_ready_delivery_type?: string;
  client_ready_delivery_message?: string;
  playable_asset_count?: number;
  final_assets_count?: number;
  final_assets?: unknown;
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

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function asArray(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.filter((item) => item && typeof item === "object").map((item) => item as Record<string, unknown>) : [];
}

function collectFallbackAssets(payload: LatestDeliverablePayload): Record<string, unknown>[] {
  const result = asRecord(payload.result);
  const data = asRecord(payload.data);
  return [
    ...asArray(payload.final_assets),
    ...asArray(payload.assets),
    ...asArray(result.final_assets),
    ...asArray(result.assets),
    ...asArray(data.final_assets),
    ...asArray(data.assets),
  ];
}

function pickString(record: Record<string, unknown>, keys: string[]): string {
  for (const key of keys) {
    const value = record[key];
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  return "";
}

function pickAssetUrl(payload: LatestDeliverablePayload): string {
  const assets = collectFallbackAssets(payload);
  const urlKeys = ["signed_preview_url", "preview_url", "signed_download_url", "download_url", "public_url", "url"];

  for (const asset of assets) {
    const ready = asset.preview_ready || asset.download_ready || asset.playable || asset.signed_delivery_created;
    const value = pickString(asset, urlKeys);
    if (ready && value) return value;
  }

  const asset: Record<string, unknown> = asRecord(payload.asset || payload.result?.asset || payload.data?.asset || {});
  return pickString(asset, urlKeys);
}

function boolFromPayload(payload: LatestDeliverablePayload | null, key: string): boolean {
  if (!payload) return false;
  const result = asRecord(payload.result);
  const data = asRecord(payload.data);
  return Boolean((payload as Record<string, unknown>)[key] || result[key] || data[key]);
}

function textFromPayload(payload: LatestDeliverablePayload | null, key: string): string {
  if (!payload) return "";
  const result = asRecord(payload.result);
  const data = asRecord(payload.data);
  return firstMeaningful((payload as Record<string, unknown>)[key], result[key], data[key]);
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
  const fallbackPackageReady = boolFromPayload(payload, "final_deliverable_ready") || boolFromPayload(payload, "client_ready_delivery");
  const fallbackPackageStatus = textFromPayload(payload, "final_deliverable_status") || textFromPayload(payload, "final_combined_asset_status");
  const fallbackPackageType = textFromPayload(payload, "final_deliverable_type") || textFromPayload(payload, "client_ready_delivery_type");
  const fallbackPackageMessage = textFromPayload(payload, "client_ready_delivery_message") || textFromPayload(payload, "final_deliverable_reason");
  const fallbackAssets = useMemo(() => (payload ? collectFallbackAssets(payload) : []), [payload]);
  const hasRealOutput = Boolean((payload?.has_real_output && (outputText || assetUrl)) || fallbackPackageReady || assetUrl);
  const status = loading
    ? "Checking latest output"
    : hasRealOutput
      ? fallbackPackageReady ? "Client-ready package" : "Completed"
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
          {fallbackPackageReady ? (
            <div className="rounded-xl border border-emerald-300/25 bg-emerald-300/10 p-4 text-sm text-emerald-50">
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-emerald-300">
                Client-ready fallback package
              </p>
              <p className="mt-2 font-semibold text-white">
                {fallbackPackageType ? fallbackPackageType.replaceAll("_", " ") : "Fallback asset package"} · {fallbackPackageStatus || "ready"}
              </p>
              {fallbackPackageMessage ? (
                <p className="mt-2 text-emerald-100">{fallbackPackageMessage}</p>
              ) : null}
              {fallbackAssets.length ? (
                <div className="mt-3 grid gap-2">
                  {fallbackAssets.slice(0, 5).map((asset, index) => (
                    <div key={`${String(asset.asset_id || index)}-${index}`} className="rounded-lg border border-emerald-300/20 bg-black/20 p-3 text-xs text-emerald-100">
                      <strong>{String(asset.asset_type || "asset")}</strong>
                      <span> · {String(asset.asset_id || "asset")}</span>
                      <span> · playable: {asset.playable ? "yes" : "no"}</span>
                      <span> · preview: {asset.preview_ready ? "yes" : "no"}</span>
                      <span> · download: {asset.download_ready ? "yes" : "no"}</span>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}

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
