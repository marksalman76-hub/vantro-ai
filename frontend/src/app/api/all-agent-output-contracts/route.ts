import { NextRequest, NextResponse } from "next/server";
import {
  ALL_AGENT_OUTPUT_CONTRACTS,
  attachAgentOutputContract,
  getAgentOutputContract,
  validateAgentOutputContract,
} from "@/lib/allAgentOutputContracts";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest): Promise<NextResponse> {
  const agentKey = req.nextUrl.searchParams.get("agent_key");

  if (agentKey) {
    return NextResponse.json({
      success: true,
      all_agent_output_contracts_enabled: true,
      contract: getAgentOutputContract(agentKey),
    }, {
      status: 200,
      headers: { "cache-control": "no-store, no-cache, must-revalidate" },
    });
  }

  return NextResponse.json({
    success: true,
    all_agent_output_contracts_enabled: true,
    contract_count: ALL_AGENT_OUTPUT_CONTRACTS.length,
    contracts: ALL_AGENT_OUTPUT_CONTRACTS,
  }, {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  let body: Record<string, unknown> = {};

  try {
    body = await req.json();
  } catch {
    body = {};
  }

  const agentKey =
    body.agent_key ||
    body.agent ||
    body.assigned_agent ||
    body.selected_agent ||
    "unknown_agent";

  const validation = validateAgentOutputContract(agentKey, body);

  return NextResponse.json(attachAgentOutputContract({
    ...body,
    agent_output_contract_validation: validation,
  }), {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
