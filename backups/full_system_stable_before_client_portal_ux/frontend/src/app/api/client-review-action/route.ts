import { NextRequest, NextResponse } from "next/server";
import { mkdir, readFile, writeFile } from "fs/promises";
import path from "path";

type ReviewAction = {
  id: string;
  action: "approved" | "rejected";
  feedback?: string;
  reason?: string;
  selected_agents?: string[];
  reviewed_item?: string;
  source?: string;
  created_at: string;
};

const DATA_DIR = path.join(process.cwd(), ".runtime-data");
const DATA_FILE = path.join(DATA_DIR, "client-review-actions.json");

async function readExistingActions(): Promise<ReviewAction[]> {
  try {
    const raw = await readFile(DATA_FILE, "utf-8");
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const action = body?.action;

    if (action !== "approved" && action !== "rejected") {
      return NextResponse.json(
        { success: false, error: "invalid_review_action" },
        { status: 400 }
      );
    }

    if (action === "rejected" && !String(body?.feedback || "").trim() && !String(body?.reason || "").trim()) {
      return NextResponse.json(
        { success: false, error: "rejection_feedback_required" },
        { status: 400 }
      );
    }

    await mkdir(DATA_DIR, { recursive: true });

    const existing = await readExistingActions();

    const event: ReviewAction = {
      id: `review_${Date.now()}`,
      action,
      feedback: String(body?.feedback || ""),
      reason: String(body?.reason || ""),
      selected_agents: Array.isArray(body?.selected_agents) ? body.selected_agents : [],
      reviewed_item: String(body?.reviewed_item || "Client deliverable"),
      source: String(body?.source || "client_workspace"),
      created_at: new Date().toISOString(),
    };

    existing.unshift(event);

    await writeFile(DATA_FILE, JSON.stringify(existing.slice(0, 250), null, 2), "utf-8");

    return NextResponse.json({
      success: true,
      event,
    });
  } catch {
    return NextResponse.json(
      { success: false, error: "review_action_failed" },
      { status: 500 }
    );
  }
}
