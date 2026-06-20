import { NextResponse } from "next/server";
import { buildDurableRuntimeStorageStatus } from "@/lib/durableRuntimeStorage";

export const dynamic = "force-dynamic";

export async function GET(): Promise<NextResponse> {
  return NextResponse.json(buildDurableRuntimeStorageStatus(), {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
