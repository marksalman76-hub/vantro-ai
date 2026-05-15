import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL || "https://ecommerce-ai-agent-platform-1.onrender.com";

export async function POST(request: NextRequest) {
  const formData = await request.formData();

  const token = String(formData.get("token") || "");
  const password = String(formData.get("password") || "");
  const confirmPassword = String(formData.get("confirm_password") || "");

  const response = await fetch(`${BACKEND_URL}/client/activate-account`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      token,
      password,
      confirm_password: confirmPassword,
    }),
  });

  const result = await response.json();

  if (!result.success) {
    return new NextResponse(`Activation failed: ${result.error}`, {
      status: 400,
    });
  }

  return NextResponse.redirect(new URL("/login", request.url));
}