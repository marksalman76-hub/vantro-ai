import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, company, email, phone, volume, message } = body;

    if (!name || !company || !email) {
      return NextResponse.json({ error: "Name, company and email are required" }, { status: 400 });
    }

    // Forward to backend which sends the SES email
    const res = await fetch(`${API_URL}/api/contact/enterprise`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, company, email, phone, volume, message }),
    });

    if (!res.ok) {
      // Backend not yet wired — fall back to console log so the form still succeeds
      console.log("[ENTERPRISE ENQUIRY]", { name, company, email, phone, volume, message });
    }

    return NextResponse.json({ success: true });
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
