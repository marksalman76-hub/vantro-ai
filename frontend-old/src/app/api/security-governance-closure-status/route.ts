import { NextResponse } from "next/server";
import { getClientSafeSecurityGovernanceStatus } from "@/lib/securityGovernanceClosure";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(getClientSafeSecurityGovernanceStatus());
}
