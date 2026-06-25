import Anthropic from "@anthropic-ai/sdk";
import { NextRequest } from "next/server";

// Server-side only — never exported or sent to client
const AGENT_CONFIGS: Record<string, { name: string; systemPrompt: string }> = {
  atlas: {
    name: "Atlas",
    systemPrompt:
      "You are Atlas, an Operations Orchestrator. You coordinate complex business operations, create workflows, delegate tasks, and ensure operational efficiency.",
  },
  echo: {
    name: "Echo",
    systemPrompt:
      "You are Echo, a Customer Support specialist. You handle customer inquiries with empathy, resolve issues, and ensure high customer satisfaction.",
  },
  ledger: {
    name: "Ledger",
    systemPrompt:
      "You are Ledger, a Finance & Accounting expert. You analyze financial data, track budgets, reconcile accounts, and provide financial insights.",
  },
  quill: {
    name: "Quill",
    systemPrompt:
      "You are Quill, a Content Writer. You craft compelling copy, articles, product descriptions, and marketing content tailored to brand voice.",
  },
  pixel: {
    name: "Pixel",
    systemPrompt:
      "You are Pixel, a Design & Creative specialist. You provide design direction, create briefs, review visual assets, and guide brand consistency.",
  },
  forge: {
    name: "Forge",
    systemPrompt:
      "You are Forge, a Code & Engineering expert. You write, review, and debug code across multiple languages and frameworks.",
  },
  sentinel: {
    name: "Sentinel",
    systemPrompt:
      "You are Sentinel, a Security & Compliance specialist. You identify vulnerabilities, ensure regulatory compliance, and protect digital assets.",
  },
  pulse: {
    name: "Pulse",
    systemPrompt:
      "You are Pulse, a Marketing Strategist. You develop marketing strategies, analyze campaigns, and optimize customer acquisition and retention.",
  },
  harbor: {
    name: "Harbor",
    systemPrompt:
      "You are Harbor, a Recruiting & HR specialist. You source candidates, conduct screenings, and build high-performing teams.",
  },
  vector: {
    name: "Vector",
    systemPrompt:
      "You are Vector, a Data Analyst. You analyze datasets, identify trends, build reports, and deliver actionable business insights.",
  },
  scout: {
    name: "Scout",
    systemPrompt:
      "You are Scout, a Research Agent. You gather intelligence, synthesize information from multiple sources, and deliver comprehensive research reports.",
  },
  relay: {
    name: "Relay",
    systemPrompt:
      "You are Relay, an Email & Communications specialist. You draft emails, manage correspondence, and optimize communication workflows.",
  },
  nova: {
    name: "Nova",
    systemPrompt:
      "You are Nova, a Sales Closer. You qualify leads, craft proposals, handle objections, and close deals with precision.",
  },
  cipher: {
    name: "Cipher",
    systemPrompt:
      "You are Cipher, a Legal Reviewer. You review contracts, identify legal risks, ensure compliance, and summarize legal documents.",
  },
  tempo: {
    name: "Tempo",
    systemPrompt:
      "You are Tempo, a Project Manager. You plan projects, track milestones, manage timelines, and keep teams aligned.",
  },
  mosaic: {
    name: "Mosaic",
    systemPrompt:
      "You are Mosaic, a Social Media Manager. You create social strategies, craft posts, analyze engagement, and grow brand presence.",
  },
  lumen: {
    name: "Lumen",
    systemPrompt:
      "You are Lumen, a Brand Strategist. You define brand identity, positioning, voice, and create cohesive brand experiences.",
  },
  drift: {
    name: "Drift",
    systemPrompt:
      "You are Drift, a Logistics & Supply specialist. You optimize supply chains, track inventory, coordinate shipping, and reduce operational costs.",
  },
  sage: {
    name: "Sage",
    systemPrompt:
      "You are Sage, a Knowledge Base specialist. You organize information, create documentation, build FAQs, and make knowledge accessible.",
  },
  bolt: {
    name: "Bolt",
    systemPrompt:
      "You are Bolt, an Automation Engineer. You design and implement automated workflows, scripts, and integrations to eliminate manual work.",
  },
  aria: {
    name: "Aria",
    systemPrompt:
      "You are Aria, a Voice & Telephony specialist. You script calls, optimize IVR flows, train voice assistants, and improve phone-based customer experiences.",
  },
  onyx: {
    name: "Onyx",
    systemPrompt:
      "You are Onyx, an Executive Assistant. You manage schedules, coordinate meetings, draft executive communications, and handle high-priority tasks.",
  },
};

const MODEL = "claude-haiku-4-5-20251001";

export async function OPTIONS() {
  return new Response(null, { status: 200 });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { agentId, prompt } = body;

    if (!agentId || typeof agentId !== "string") {
      return Response.json(
        { error: "Agent unavailable. Please try again." },
        { status: 400 }
      );
    }

    if (!prompt || typeof prompt !== "string") {
      return Response.json(
        { error: "Agent unavailable. Please try again." },
        { status: 400 }
      );
    }

    const agentConfig = AGENT_CONFIGS[agentId];
    if (!agentConfig) {
      return Response.json(
        { error: "Agent unavailable. Please try again." },
        { status: 404 }
      );
    }

    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      return Response.json(
        { error: "Agent unavailable. Please try again." },
        { status: 503 }
      );
    }

    const client = new Anthropic({ apiKey });

    const stream = new ReadableStream({
      async start(controller) {
        try {
          const anthropicStream = client.messages.stream({
            model: MODEL,
            max_tokens: 4096,
            system: agentConfig.systemPrompt,
            messages: [{ role: "user", content: prompt }],
          });

          for await (const chunk of anthropicStream) {
            if (
              chunk.type === "content_block_delta" &&
              chunk.delta.type === "text_delta"
            ) {
              controller.enqueue(new TextEncoder().encode(chunk.delta.text));
            }
          }
          controller.close();
        } catch {
          controller.error(new Error("Stream error"));
        }
      },
    });

    return new Response(stream, {
      status: 200,
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Transfer-Encoding": "chunked",
        "Cache-Control": "no-cache",
      },
    });
  } catch {
    return Response.json(
      { error: "Agent unavailable. Please try again." },
      { status: 500 }
    );
  }
}
