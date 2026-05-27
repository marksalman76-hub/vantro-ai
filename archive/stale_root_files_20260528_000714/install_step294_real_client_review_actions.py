from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
API_DIR = ROOT / "frontend" / "src" / "app" / "api" / "client-review-action"
API_FILE = API_DIR / "route.ts"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)
API_DIR.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step294_real_review_actions_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

# Add state
state_target = '''  const [feedbackReason, setFeedbackReason] = useState("");
  const [executionState, setExecutionState] = useState<"idle" | "running" | "completed" | "rejected">("idle");'''

state_replacement = '''  const [feedbackReason, setFeedbackReason] = useState("");
  const [reviewStatus, setReviewStatus] = useState<"pending" | "approved" | "rejected">("pending");
  const [reviewActionLoading, setReviewActionLoading] = useState(false);
  const [executionState, setExecutionState] = useState<"idle" | "running" | "completed" | "rejected">("idle");'''

if state_target not in text:
    raise SystemExit("ERROR: state target not found.")

text = text.replace(state_target, state_replacement)

# Add helper function
helper_target = '''  const toggleAgent = (agent: string) => {'''

helper_code = '''  async function recordClientReviewAction(action: "approved" | "rejected", feedback = "", reason = "") {
    setReviewActionLoading(true);

    try {
      const response = await fetch("/api/client-review-action", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          action,
          feedback,
          reason,
          selected_agents: selectedAgents,
          reviewed_item: "Luxury skincare launch campaign",
          source: "client_workspace",
        }),
      });

      if (!response.ok) {
        throw new Error("Review action failed");
      }

      const data = await response.json();

      if (!data?.success) {
        throw new Error("Review action was not accepted");
      }

      return true;
    } catch {
      setToastMessage("Review action could not be saved. Please try again.");
      return false;
    } finally {
      setReviewActionLoading(false);
    }
  }

'''

if "async function recordClientReviewAction" not in text:
    text = text.replace(helper_target, helper_code + helper_target)

# Update approve action
text = text.replace(
'''                    onClick={() => {
                      setExecutionState("completed");
                      setToastMessage("Deliverable approved. Execution is ready to continue.");
                    }}''',
'''                    onClick={async () => {
                      const saved = await recordClientReviewAction("approved");
                      if (!saved) return;

                      setReviewStatus("approved");
                      setExecutionState("completed");
                      setToastMessage("Deliverable approved and saved to the client review log.");
                    }}'''
)

# Update rejection submit action
text = text.replace(
'''                onClick={() => {
                  if (!feedbackText.trim() && !feedbackReason) return;
                  setShowRejectModal(false);
                  setToastMessage("Feedback submitted. The agent will use it to improve the next output.");
                }}''',
'''                onClick={async () => {
                  if (!feedbackText.trim() && !feedbackReason) return;

                  const saved = await recordClientReviewAction("rejected", feedbackText, feedbackReason);
                  if (!saved) return;

                  setReviewStatus("rejected");
                  setShowRejectModal(false);
                  setToastMessage("Revision request saved. Feedback has been added to the client review log.");
                }}'''
)

# Make completed pill dynamic
text = text.replace(
'''                Completed''',
'''                {reviewStatus === "approved" ? "Approved" : reviewStatus === "rejected" ? "Revision requested" : "Completed"}''',
1
)

# Add loading label to submit button
text = text.replace(
'''                Submit feedback
              </button>''',
'''                {reviewActionLoading ? "Saving..." : "Submit feedback"}
              </button>'''
)

# Add loading label to approve button
text = text.replace(
'''                    👍 Approve
                  </button>''',
'''                    {reviewActionLoading ? "Saving..." : "👍 Approve"}
                  </button>'''
)

PAGE.write_text(text, encoding="utf-8")

API_FILE.write_text('''import { NextRequest, NextResponse } from "next/server";
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
''', encoding="utf-8")

print("STEP_294_REAL_CLIENT_REVIEW_ACTIONS_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {API_FILE}")
print("STEP_294_OK")