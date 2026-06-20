import { NextResponse } from "next/server";
import { getRegressionTestSuiteStatus } from "@/lib/regressionTestSuiteStatus";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(getRegressionTestSuiteStatus());
}
