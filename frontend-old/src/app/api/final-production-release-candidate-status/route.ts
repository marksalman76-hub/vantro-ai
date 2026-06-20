import { NextResponse } from "next/server";
import { getFinalProductionReleaseCandidateStatus } from "@/lib/finalProductionReleaseCandidate";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(getFinalProductionReleaseCandidateStatus());
}
