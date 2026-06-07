import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_BASE_URL =
  process.env.BACKEND_BASE_URL ||
  process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
  "https://api.trance-formation.com.au";

function clientHeaders(): Record<string, string> {
  return {
    "Content-Type": "application/json",
    "Cache-Control": "no-store",
    "x-actor-role": "client",
  };
}

export async function POST(request: NextRequest) {
  try {
    const payload = await request.json();

    const response = await fetch(`${BACKEND_BASE_URL}/client/creative/product-assets/upload`, {
      method: "POST",
      cache: "no-store",
      headers: clientHeaders(),
      body: JSON.stringify({
        ...payload,
        uploaded_by: "client",
      }),
    });

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
      headers: { "Cache-Control": "no-store" },
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        layer: "frontend_client_creative_product_assets_upload_proxy",
        status: "proxy_error",
        authority: "backend_canonical",
        production_fail_closed: process.env.NODE_ENV === "production",
        error: error instanceof Error ? error.message : String(error),
        credential_values_exposed: false,
      },
      { status: 500 }
    );
  }
}
