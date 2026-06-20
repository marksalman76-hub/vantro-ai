import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://api.trance-formation.com.au";

export async function POST(request: NextRequest) {
  const formData = await request.formData();

  const token = String(formData.get("token") || "");
  const password = String(formData.get("password") || "");
  const confirmPassword = String(formData.get("confirm_password") || "");

  if (!token) {
    return NextResponse.json(
      { success: false, error: "activation_token_required" },
      { status: 400 }
    );
  }

  const response = await fetch(`${BACKEND_URL}/client/activate-account`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-tenant-id": "public_activation",
      "x-actor-role": "customer",
      "Origin": "https://ecommerce-ai-agent-platform.vercel.app",
      "Referer": "https://ecommerce-ai-agent-platform.vercel.app/activate",
    },
    body: JSON.stringify({
      token,
      password,
      confirm_password: confirmPassword,
    }),
    cache: "no-store",
  });

  const result = await response.json().catch(() => ({
    success: false,
    error: "activation_backend_response_not_json",
  }));

  if (!response.ok || !result.success) {
    return NextResponse.json(
      {
        success: false,
        error: result.error || "activation_failed",
        backend_status: response.status,
        backend_result: result,
      },
      { status: 400 }
    );
  }

  return NextResponse.redirect(
    new URL("/login?activated=1", request.url),
    { status: 303 }
  );
}
