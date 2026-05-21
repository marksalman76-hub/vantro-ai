import { NextResponse } from "next/server";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.BACKEND_URL ||
  "http://127.0.0.1:8000";

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const payload = {
      tenant_id: body.tenant_id || `signup_${Date.now()}`,
      customer_email: body.customer_email,
      target_package: body.target_package,
      selected_agents: body.selected_agents || [],
      success_url_path: "/client/billing/success",
      cancel_url_path: "/signup",
    };

    const response = await fetch(`${BACKEND_URL}/billing/live-checkout-session`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-tenant-id": "public_signup",
        "x-actor-role": "customer",
      },
      body: JSON.stringify(payload),
      cache: "no-store",
    });

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json(
      {
        success: false,
        error: "checkout_request_failed",
      },
      { status: 500 }
    );
  }
}
