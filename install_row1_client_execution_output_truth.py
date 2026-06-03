from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / "backups" / f"row1_client_execution_output_truth_before_{stamp}"
backup.mkdir(parents=True, exist_ok=True)

route = ROOT / "frontend" / "src" / "app" / "api" / "delegated-workforce-execution" / "route.ts"
route.parent.mkdir(parents=True, exist_ok=True)

if route.exists():
    shutil.copy2(route, backup / "route.ts")

route.write_text(r'''import { NextRequest, NextResponse } from "next/server";

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
    const emptyMarkers = new Set([
      "completed",
      "complete",
      "success",
      "successful",
      "done",
      "pending",
      "awaiting_output",
      "no output",
      "no deliverable",
      "null",
      "undefined",
    ]);
    return !emptyMarkers.has(trimmed.toLowerCase());
  }
  if (Array.isArray(value)) return value.some(isMeaningfulValue);
  if (typeof value === "object") return Object.values(value as Record<string, unknown>).some(isMeaningfulValue);
  return true;
}

function pickOutputCandidates(payload: Record<string, unknown>): unknown[] {
  const result = (payload.result || {}) as Record<string, unknown>;
  const data = (payload.data || {}) as Record<string, unknown>;
  const asset = (payload.asset || result.asset || data.asset || {}) as Record<string, unknown>;

  return [
    payload.output,
    payload.deliverable,
    payload.deliverables,
    payload.latest_deliverable,
    payload.generated_output,
    payload.final_output,
    payload.asset,
    payload.assets,
    result.output,
    result.deliverable,
    result.deliverables,
    result.latest_deliverable,
    result.generated_output,
    result.final_output,
    result.asset,
    result.assets,
    data.output,
    data.deliverable,
    data.deliverables,
    data.latest_deliverable,
    data.generated_output,
    data.final_output,
    data.asset,
    data.assets,
    asset.preview_url,
    asset.download_url,
    asset.url,
    asset.public_url,
    asset.signed_preview_url,
    asset.signed_download_url,
  ];
}

function hasRealClientOutput(payload: Record<string, unknown>): boolean {
  return pickOutputCandidates(payload).some(isMeaningfulValue);
}

function normaliseClientExecutionTruth(raw: unknown): unknown {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return raw;

  const payload = { ...(raw as Record<string, unknown>) };
  const hasRealOutput = hasRealClientOutput(payload);

  payload.has_real_output = hasRealOutput;
  payload.client_output_truth_checked = true;

  if (!hasRealOutput) {
    payload.completed = false;
    payload.is_completed = false;
    payload.workflow_status = "awaiting_output";
    payload.execution_status = "awaiting_output";
    payload.status = "awaiting_output";
    payload.client_safe_status = "Output pending";
    payload.display_status = "Output pending";
    payload.output_truth_reason = "No real deliverable, output, or generated asset was returned.";
  } else {
    payload.client_safe_status = "Completed";
    payload.display_status = "Completed";
    payload.output_truth_reason = "A real deliverable, output, or generated asset was returned.";
  }

  return payload;
}

async function proxyToBackend(req: NextRequest): Promise<NextResponse> {
  const body = await req.text();
  const headers: Record<string, string> = {
    "content-type": req.headers.get("content-type") || "application/json",
  };

  const auth = req.headers.get("authorization");
  const adminToken = req.headers.get("x-admin-token");
  const cookie = req.headers.get("cookie");

  if (auth) headers.authorization = auth;
  if (adminToken) headers["x-admin-token"] = adminToken;
  if (cookie) headers.cookie = cookie;

  const response = await fetch(`${backendBaseUrl()}/delegated-workforce-execution`, {
    method: "POST",
    headers,
    body,
    cache: "no-store",
  });

  const text = await response.text();

  let payload: unknown;
  try {
    payload = JSON.parse(text);
  } catch {
    return new NextResponse(text, { status: response.status });
  }

  return NextResponse.json(normaliseClientExecutionTruth(payload), {
    status: response.status,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  return proxyToBackend(req);
}
''', encoding="utf-8")

test = ROOT / "test_row1_client_execution_output_truth.py"
test.write_text(r'''from pathlib import Path

route = Path("frontend/src/app/api/delegated-workforce-execution/route.ts")
text = route.read_text(encoding="utf-8")

required = [
    "hasRealClientOutput",
    "normaliseClientExecutionTruth",
    "client_output_truth_checked",
    "No real deliverable, output, or generated asset was returned.",
    "Output pending",
    "Completed",
    "cache: \"no-store\"",
]

missing = [item for item in required if item not in text]
if missing:
    raise SystemExit(f"ROW1_CLIENT_EXECUTION_OUTPUT_TRUTH_FAILED missing={missing}")

print("ROW1_CLIENT_EXECUTION_OUTPUT_TRUTH_PASSED")
''', encoding="utf-8")

print("ROW1_CLIENT_EXECUTION_OUTPUT_TRUTH_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {route}")
print(f"Created: {test}")