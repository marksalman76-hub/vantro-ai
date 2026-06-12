import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type ParallelMediaJobRequest = {
  prompt?: string;
  task?: string;
  media_type?: string;
  duration_seconds?: number;
  aspect_ratio?: string;
  quality_mode?: string;
  creative_controls?: Record<string, unknown>;
  human_mode?: string;
  selected_agent?: string;
  selected_agents?: string[];
  agent_ids?: string[];
  multi_agent_media_execution?: boolean;
  source?: string;
  client_id?: string;
  admin_request?: boolean;
};

function normalizeString(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

function normalizeStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .map((item) => normalizeString(item))
    .filter((item) => item.length > 0);
}

function makeJobId(): string {
  const randomPart =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID().replace(/-/g, "").slice(0, 12)
      : Math.random().toString(16).slice(2, 14);

  return `parallel_media_job_${Date.now()}_${randomPart}`;
}

function buildAgentSelection(payload: ParallelMediaJobRequest) {
  const selectedAgent = normalizeString(payload.selected_agent);
  const selectedAgents = normalizeStringArray(payload.selected_agents);
  const agentIds = normalizeStringArray(payload.agent_ids);

  const merged = Array.from(
    new Set(
      [
        selectedAgent,
        ...selectedAgents,
        ...agentIds,
      ].filter((item) => item.length > 0),
    ),
  );

  const leadAgent = selectedAgent || merged[0] || "auto";

  return {
    selected_agent: leadAgent,
    selected_agents: merged.length > 0 ? merged : [leadAgent],
    agent_ids: merged.length > 0 ? merged : [leadAgent],
    multi_agent_media_execution:
      Boolean(payload.multi_agent_media_execution) || merged.length > 1,
  };
}

export async function GET() {
  return NextResponse.json({
    success: true,
    route: "parallel-media-jobs",
    status: "foundation_ready",
    message:
      "Parallel media job API foundation is available. This route does not replace the working Create Media popup execution path.",
    preserves_working_popup: true,
    supported_next_steps: [
      "durable job persistence",
      "queue enqueue bridge",
      "status polling",
      "asset result hydration",
      "admin diagnostics",
      "client-safe result visibility",
    ],
  });
}

export async function POST(request: NextRequest) {
  let payload: ParallelMediaJobRequest;

  try {
    payload = await request.json();
  } catch {
    return NextResponse.json(
      {
        success: false,
        error: "invalid_json",
        message: "Request body must be valid JSON.",
      },
      { status: 400 },
    );
  }

  const prompt = normalizeString(payload.prompt || payload.task);

  if (!prompt) {
    return NextResponse.json(
      {
        success: false,
        error: "missing_prompt",
        message: "A prompt or task is required to create a parallel media job.",
      },
      { status: 400 },
    );
  }

  const agentSelection = buildAgentSelection(payload);
  const now = new Date().toISOString();

  const job = {
    job_id: makeJobId(),
    status: "accepted_foundation",
    created_at: now,
    updated_at: now,
    execution_mode: "parallel_media_foundation",
    popup_replacement: false,
    preserves_working_popup: true,
    prompt,
    media_type: normalizeString(payload.media_type) || "video",
    duration_seconds:
      typeof payload.duration_seconds === "number" && payload.duration_seconds > 0
        ? payload.duration_seconds
        : null,
    aspect_ratio: normalizeString(payload.aspect_ratio) || null,
    quality_mode: normalizeString(payload.quality_mode) || null,
    human_mode: normalizeString(payload.human_mode) || null,
    creative_controls:
      payload.creative_controls && typeof payload.creative_controls === "object"
        ? payload.creative_controls
        : {},
    source: normalizeString(payload.source) || "api.parallel-media-jobs.foundation",
    client_id: normalizeString(payload.client_id) || null,
    admin_request: Boolean(payload.admin_request),
    ...agentSelection,
    next_required_integration: {
      durable_storage: false,
      queue_enqueue: false,
      worker_execution: false,
      popup_status_polling: false,
      final_asset_display: false,
    },
  };

  return NextResponse.json(
    {
      success: true,
      accepted: true,
      job,
      message:
        "Parallel media job accepted by foundation route only. Existing Create Media popup execution remains unchanged.",
    },
    { status: 202 },
  );
}
