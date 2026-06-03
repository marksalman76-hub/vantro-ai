import { NextResponse } from "next/server";
import { getSecurityGovernanceClosureStatus } from "@/lib/securityGovernanceClosure";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(getSecurityGovernanceClosureStatus());
}
