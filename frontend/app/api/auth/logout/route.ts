import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

export async function POST(request: NextRequest) {
  try {
    await fetch(`${API_URL}/api/auth/logout`, { method: "POST" });
  } catch {
    // Non-fatal — always clear the cookie regardless
  }
  const response = NextResponse.json({ message: "Logged out" });
  response.cookies.delete("access_token");
  return response;
}
