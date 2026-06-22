import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, company, email, phone, volume, message } = body;

    if (!name || !company || !email) {
      return NextResponse.json({ error: "Name, company and email are required" }, { status: 400 });
    }

    // Log the enquiry — connect to email/CRM later
    console.log("[ENTERPRISE ENQUIRY]", {
      name, company, email,
      phone: phone || "—",
      volume: volume || "—",
      message: message || "—",
      receivedAt: new Date().toISOString(),
    });

    // TODO: send email via SES/SendGrid or post to Slack/CRM
    // await sendEmail({ to: "hello@vantro.ai", subject: `Enterprise enquiry from ${company}`, ... })

    return NextResponse.json({ success: true });
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
