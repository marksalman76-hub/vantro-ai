import { NextResponse } from "next/server";
import { getClientSafeProductionMonitoringIncidentReadinessStatus } from "@/lib/productionMonitoringIncidentReadiness";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(getClientSafeProductionMonitoringIncidentReadinessStatus());
}
