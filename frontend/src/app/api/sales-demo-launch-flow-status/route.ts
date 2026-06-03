import { NextResponse } from "next/server";
import { getSalesDemoLaunchFlowStatus } from "@/lib/salesDemoLaunchFlow";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(getSalesDemoLaunchFlowStatus());
}
