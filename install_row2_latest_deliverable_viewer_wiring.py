from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / "backups" / f"row2_latest_deliverable_viewer_before_{stamp}"
backup.mkdir(parents=True, exist_ok=True)

client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
component = ROOT / "frontend" / "src" / "app" / "client" / "LatestDeliverableViewer.tsx"
api_route = ROOT / "frontend" / "src" / "app" / "api" / "client-latest-deliverable" / "route.ts"

for p in [client_page, component, api_route]:
    if p.exists():
        shutil.copy2(p, backup / p.name)

component.write_text(r'''"use client";

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
  const asset = payload.asset || payload.result?.asset || payload.data?.asset || {};
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
''', encoding="utf-8")

api_route.parent.mkdir(parents=True, exist_ok=True)
api_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

function backendBaseUrl(): string {
  return (
    process.env.BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "https://api.trance-formation.com.au"
  ).replace(/\/$/, "");
}

function isMeaningfulValue(value: unknown): boolean {
  if (value === null || value === undefined) return false;
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) return false;
    return !["completed", "complete", "success", "successful", "done", "pending", "null", "undefined"].includes(trimmed.toLowerCase());
  }
  if (Array.isArray(value)) return value.some(isMeaningfulValue);
  if (typeof value === "object") return Object.values(value as Record<string, unknown>).some(isMeaningfulValue);
  return true;
}

function normalise(payload: Record<string, unknown>): Record<string, unknown> {
  const result = (payload.result || {}) as Record<string, unknown>;
  const data = (payload.data || {}) as Record<string, unknown>;
  const asset = (payload.asset || result.asset || data.asset || {}) as Record<string, unknown>;

  const candidates = [
    payload.output, payload.deliverable, payload.latest_deliverable, payload.generated_output, payload.final_output,
    result.output, result.deliverable, result.latest_deliverable, result.generated_output, result.final_output,
    data.output, data.deliverable, data.latest_deliverable, data.generated_output, data.final_output,
    payload.asset, payload.assets, result.asset, result.assets, data.asset, data.assets,
    asset.preview_url, asset.download_url, asset.url, asset.public_url, asset.signed_preview_url, asset.signed_download_url,
  ];

  const hasRealOutput = candidates.some(isMeaningfulValue);

  return {
    ...payload,
    has_real_output: hasRealOutput,
    client_output_truth_checked: true,
    client_safe_status: hasRealOutput ? "Completed" : "Output pending",
    display_status: hasRealOutput ? "Completed" : "Output pending",
    output_truth_reason: hasRealOutput
      ? "A real deliverable, output, or generated asset was returned."
      : "No real deliverable, output, or generated asset was returned.",
  };
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  const headers: Record<string, string> = {};
  const auth = req.headers.get("authorization");
  const adminToken = req.headers.get("x-admin-token");
  const cookie = req.headers.get("cookie");

  if (auth) headers.authorization = auth;
  if (adminToken) headers["x-admin-token"] = adminToken;
  if (cookie) headers.cookie = cookie;

  const response = await fetch(`${backendBaseUrl()}/client-latest-deliverable`, {
    method: "GET",
    headers,
    cache: "no-store",
  });

  const text = await response.text();

  let payload: unknown;
  try {
    payload = JSON.parse(text);
  } catch {
    return NextResponse.json({
      success: false,
      has_real_output: false,
      client_output_truth_checked: true,
      client_safe_status: "Output pending",
      display_status: "Output pending",
      output_truth_reason: "Latest deliverable route did not return JSON.",
    }, { status: response.status });
  }

  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return NextResponse.json({
      success: false,
      has_real_output: false,
      client_output_truth_checked: true,
      client_safe_status: "Output pending",
      display_status: "Output pending",
      output_truth_reason: "Latest deliverable response was empty.",
    }, { status: response.status });
  }

  return NextResponse.json(normalise(payload as Record<string, unknown>), {
    status: response.status,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
''', encoding="utf-8")

page = client_page.read_text(encoding="utf-8")

if 'LatestDeliverableViewer from "./LatestDeliverableViewer"' not in page:
    lines = page.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, 'import LatestDeliverableViewer from "./LatestDeliverableViewer";')
    page = "\n".join(lines) + "\n"

viewer_block = '''
      <LatestDeliverableViewer />
'''

if "<LatestDeliverableViewer />" not in page:
    if "</main>" in page:
        page = page.replace("</main>", viewer_block + "    </main>", 1)
    else:
        marker = "export default"
        if marker not in page:
            raise SystemExit("CLIENT_PAGE_INJECTION_FAILED: client page format not recognised.")
        raise SystemExit("CLIENT_PAGE_INJECTION_FAILED: no </main> tag found for safe insertion.")

client_page.write_text(page, encoding="utf-8")

test = ROOT / "test_row2_latest_deliverable_viewer_wiring.py"
test.write_text(r'''from pathlib import Path

client_page = Path("frontend/src/app/client/page.tsx")
component = Path("frontend/src/app/client/LatestDeliverableViewer.tsx")
api_route = Path("frontend/src/app/api/client-latest-deliverable/route.ts")

checks = {
    str(client_page): [
        'LatestDeliverableViewer from "./LatestDeliverableViewer"',
        '<LatestDeliverableViewer />',
    ],
    str(component): [
        'Latest deliverable',
        'Client output viewer',
        'has_real_output',
        'Preview latest asset',
        'No real deliverable, output, or generated asset exists yet.',
    ],
    str(api_route): [
        'client_output_truth_checked',
        'has_real_output',
        'Output pending',
        'Completed',
        'cache: "no-store"',
    ],
}

missing = {}
for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW2_LATEST_DELIVERABLE_VIEWER_WIRING_FAILED missing={missing}")

print("ROW2_LATEST_DELIVERABLE_VIEWER_WIRING_PASSED")
''', encoding="utf-8")

print("ROW2_LATEST_DELIVERABLE_VIEWER_WIRED")
print(f"Backup: {backup}")
print(f"Updated: {client_page}")
print(f"Created/updated: {component}")
print(f"Created/updated: {api_route}")
print(f"Created: {test}")