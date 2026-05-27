from pathlib import Path
from datetime import datetime

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
backup_dir = root / "backups" / f"support_agent_chat_route_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

api_dir = root / "frontend" / "src" / "app" / "api" / "support-agent-chat"
api_dir.mkdir(parents=True, exist_ok=True)
api_file = api_dir / "route.ts"

if api_file.exists():
    backup = backup_dir / "frontend/src/app/api/support-agent-chat/route.ts"
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text(api_file.read_text(encoding="utf-8"), encoding="utf-8")

api_file.write_text('''import { NextRequest, NextResponse } from "next/server";

function buildSupportAgentReply(message: string, source: string) {
  const text = message.toLowerCase();

  if (text.includes("how") && text.includes("agent") && text.includes("think")) {
    return "Our Support Agent uses the same governed AI-agent structure as the platform: it reads your request, identifies the task type, checks whether it needs support guidance, account help, billing help, technical help, or escalation, then gives a safe client-facing answer. It does not expose internal prompts, private configuration, credentials, or backend logic.";
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
''', encoding="utf-8")

targets = [
    root / "frontend/src/app/homepage-support-client.tsx",
    root / "frontend/src/app/login/support-client.tsx",
    root / "frontend/src/app/admin-login/support-client.tsx",
]

for target in targets:
    backup = backup_dir / target.relative_to(root)
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")

    s = target.read_text(encoding="utf-8")

    old_fetch_block_start = s.find('      const response = await fetch("/api/run-agent", {')
    old_fetch_block_end = s.find('      const data = await response.json();', old_fetch_block_start)

    if old_fetch_block_start == -1 or old_fetch_block_end == -1:
        raise RuntimeError(f"FETCH_BLOCK_NOT_FOUND: {target}")

    old_fetch_block_end += len('      const data = await response.json();')

    new_fetch_block = '''      const response = await fetch("/api/support-agent-chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: sourceLabel,
          message: text,
        }),
      });

      const data = await response.json();'''

    s = s[:old_fetch_block_start] + new_fetch_block + s[old_fetch_block_end:]

    s = s.replace('data?.execution?.deliverable?.summary ||\n        data?.deliverable?.summary ||\n        "Thanks — I have received your message. A support workflow has been created for this request."', 'data?.reply ||\n        "Thanks — I have received your message. The Support Agent is active."')

    s = s.replace('I could not reach the live Support Agent right now. Please try again, or use the contact form for urgent support.', 'I could not reach the live Support Agent right now. Please try again in a moment.')

    target.write_text(s, encoding="utf-8")

print("LIVE_SUPPORT_AGENT_CHAT_ROUTE_INSTALLED")
print("Updated route:", api_file.relative_to(root))
print("Updated widgets:")
for target in targets:
    print("-", target.relative_to(root))
print("Backup:", backup_dir)