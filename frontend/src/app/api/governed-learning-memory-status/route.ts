import { NextResponse } from "next/server";
import { getClientSafeGovernedLearningMemoryStatus } from "@/lib/governedLearningMemory";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(getClientSafeGovernedLearningMemoryStatus());
}
