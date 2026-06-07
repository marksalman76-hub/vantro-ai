import { NextRequest, NextResponse } from "next/server";

function buildSupportAgentReply(message: string, source: string) {
  const text = message.toLowerCase();

  if (text.includes("how") && text.includes("agent") && text.includes("think")) {
    return "Our Support Agent can help with platform questions, onboarding, account access, billing, agent usage, workflow issues, and support escalation. It provides clear customer-safe guidance without exposing private configuration, credentials, or restricted platform details.";
  }

  if (text.includes("password") || text.includes("login") || text.includes("access")) {
    return "I can help with access issues. For password or login problems, use the reset password/contact support link and include your account email. If you are an admin, use the owner/admin access flow only.";
  }

  if (text.includes("billing") || text.includes("payment") || text.includes("subscription")) {
    return "For billing or subscription support, include your account email, selected package, and the issue you are seeing. I can help route the request to the right support workflow.";
  }

  if (text.includes("agent") || text.includes("automation") || text.includes("workflow")) {
    return "I can help with agent and workflow questions. Tell me which agent you are using, what you expected it to do, and what output or action you received.";
  }

  return `Thanks — I’m the live Support Agent for ${source}. I can help with account access, billing, agent usage, workflow issues, onboarding, and escalation. Please share the issue and the account email if it relates to a specific workspace.`;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const message = String(body?.message || "").trim();
    const source = String(body?.source || "this page").trim();

    if (!message) {
      return NextResponse.json(
        { success: false, error: "message_required" },
        { status: 400 }
      );
    }

    return NextResponse.json({
      success: true,
      agent: "support_agent",
      source,
      reply: buildSupportAgentReply(message, source),
      live_chat: true,
      routed_to_contact_form: false,
    });
  } catch {
    return NextResponse.json(
      { success: false, error: "support_agent_chat_failed" },
      { status: 500 }
    );
  }
}
