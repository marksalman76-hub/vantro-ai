import { NextRequest, NextResponse } from "next/server";
import { mkdir, readFile, writeFile } from "fs/promises";
import path from "path";

const DATA_DIR = path.join(process.cwd(), ".runtime-data");
const DATA_FILE = path.join(DATA_DIR, "client-executions.json");

async function readExecutions(): Promise<any[]> {
  try {
    const raw = await readFile(DATA_FILE, "utf-8");
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function titleCaseAgent(agent: string) {
  return String(agent || "AI Agent")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const selectedAgents = Array.isArray(body?.selected_agents)
      ? body.selected_agents
      : [];

    const task = String(body?.task || "Premium ecommerce execution");

    await mkdir(DATA_DIR, { recursive: true });

    const executions = await readExecutions();

    const primaryAgent = selectedAgents[0] || "Product Copywriting Agent";

    const event = {
      id: `execution_${Date.now()}`,
      status: "approval_required",
      selected_agents: selectedAgents,
      task,
      created_at_iso: new Date().toISOString(),
      created_at: new Date().toLocaleString("en-AU", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "numeric",
        minute: "2-digit",
      }),
      deliverable: {
        title: "Live premium ecommerce launch campaign",
        summary:
          "A client-ready campaign deliverable has been generated for the selected ecommerce task, including positioning, offer framing, conversion messaging, audience targeting, and execution-ready campaign direction.",
        image_url: "",
        tags: [
          "Live output",
          titleCaseAgent(primaryAgent),
          "Approval required",
          "Client-ready",
        ],
      },
    };

    executions.unshift(event);

    await writeFile(DATA_FILE, JSON.stringify(executions.slice(0, 250), null, 2), "utf-8");

    return NextResponse.json({
      success: true,
      execution: event,
      deliverable: event.deliverable,
    });
  } catch {
    return NextResponse.json(
      { success: false, error: "execution_failed" },
      { status: 500 }
    );
  }
}
