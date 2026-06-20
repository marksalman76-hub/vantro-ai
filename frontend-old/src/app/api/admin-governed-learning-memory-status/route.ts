import { NextResponse } from "next/server";
import { getGovernedLearningMemoryStatus } from "@/lib/governedLearningMemory";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(getGovernedLearningMemoryStatus());
}
