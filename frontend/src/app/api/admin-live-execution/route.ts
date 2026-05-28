import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_API_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.ADMIN_AUTH_SECRET ||
  "";

export async function POST(req: NextRequest) {
  if (!ADMIN_TOKEN) {
    return NextResponse.json(
      { success: false, error: "admin_token_not_configured" },
      { status: 500 }
    );
  }

  const body = await req.json();

  const requestedAgent = body.requested_agent || "marketing_specialist_agent";
  const userTask =
    body.task ||
    "Produce a commercial-quality governed live execution result.";

  const premiumTask = `
You are executing as: ${requestedAgent}.

Platform standard:
This is a unique multi-agent, multi-industry platform. Do not default to ecommerce unless the task is ecommerce-specific.
Use the industry, business model, market, customer segment, geography, and commercial intent stated in the task.

Output quality requirement:
Produce a premium, client-ready, commercially usable, execution-ready deliverable.
Do not provide generic consulting filler.
Do not merely explain concepts.
Do not say you need more information unless absolutely required; make reasonable explicit assumptions and proceed.

Agent-specific behaviour:
Stay strictly inside the selected agent's specialist role.
Produce the type of deliverable that this agent should produce in a real commercial workflow.

Required structure:
1. Executive summary
2. Business/industry context assumptions
3. Specific opportunity or problem diagnosis
4. Execution plan with concrete steps
5. Deliverables/assets/actions to create
6. KPIs or measurable success criteria
7. Risks, constraints, and mitigations
8. Owner/admin review points
9. Immediate next actions

User task:
${userTask}
`.trim();

  const payload = {
    tenant_id: "owner_admin",
    requested_agent: requestedAgent,
    workflow_stage: "admin_live_execution_premium_multi_industry",
    task: premiumTask,
    action_type: "governed_live_provider_generation",
    region: body.region || "Global",
    language: body.language || "English",
    currency: body.currency || "USD",
    owner_approved: true,
    execute_real_world_action: true,
    project_id: "admin_live_execution_output_viewer",
    actor_role: "owner_admin",
    requested_credits: 1,
    quality_gate_required: true,
    premium_output_required: true,
    gold_standard_required: true,
    business_context_required: true,
  };

  const response = await fetch(`${BACKEND_URL}/run-agent`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-admin-token": ADMIN_TOKEN,
      "x-actor-role": "owner_admin",
      "x-tenant-id": "owner_admin",
      "x-csrf-token": "admin-live-execution-output-viewer",
      origin: process.env.NEXT_PUBLIC_FRONTEND_URL || "https://trance-formation.com.au",
    },
    body: JSON.stringify(payload),
    cache: "no-store",
  });

  const data = await response.json();

  const execution = data?.execution || {};
  const adapter = execution?.adapter_result || {};
  const normalised = adapter?.normalised_response || {};
  const safeOutput = normalised?.safe_output || {};

  const normalized_output =
    safeOutput?.text ||
    data?.output?.generated_output ||
    data?.output?.output ||
    data?.output?.content ||
    data?.generated_output ||
    data?.result ||
    data?.message ||
    "";

  return NextResponse.json({
    success: response.ok && data?.success === true,
    backend_status: response.status,
    normalized_output,
    provider_key: adapter?.provider_key || "openai",
    execution_status: execution?.execution_status || data?.execution_status || data?.status || "",
    live_external_call_executed: adapter?.live_external_call_executed === true,
    latency_ms: adapter?.latency_ms || null,
    customer_safe: adapter?.customer_safe === true,
    credential_values_exposed: adapter?.credential_values_exposed === true,
    data,
  });
}
