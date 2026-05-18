import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://ecommerce-ai-agent-platform-1.onrender.com";

export async function GET() {
  const cookieStore = await cookies();
  const sessionToken = cookieStore.get("client_session")?.value;

  if (!sessionToken) {
    return NextResponse.json(
      {
        success: false,
        error: "client_session_missing",
      },
      { status: 401 }
    );
  }

  const response = await fetch(
    `${BACKEND_URL}/client/me?session_token=${encodeURIComponent(sessionToken)}`,
    {
      method: "GET",
      cache: "no-store",
    }
  );

  const data = await response.json().catch(() => ({
    success: false,
    error: "invalid_backend_response",
  }));

  return NextResponse.json(data, { status: response.status });
}
