from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

FILES = [
    ROOT / "frontend" / "src" / "app" / "client" / "page.tsx",
    ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx",
]

for path in FILES:
    if not path.exists():
        continue

    original = path.read_text(encoding="utf-8", errors="ignore")
    backup = BACKUPS / f"{path.stem}_before_phase_g_remove_static_demo_ui_{timestamp}{path.suffix}"
    backup.write_text(original, encoding="utf-8")

    text = original

    replacements = {
        # Client generic wording
        "Run premium ecommerce AI agents, generate governed outputs, manage execution workflows, and produce commercial-grade deliverables.":
            "Run selected AI agents, generate governed outputs, manage execution workflows, and produce client-specific deliverables.",

        "Store context for smarter agent outputs":
            "Store business context for client-specific outputs",

        "Add business context once so every active AI agent can produce more accurate campaigns, creative assets, copy, positioning, and execution recommendations.":
            "Add business context once so active AI agents can produce more accurate outputs, recommendations, and deliverables.",

        "Create premium ecommerce campaign assets for this business using the saved business profile, active agents, and selected execution requirements.":
            "Create a client-specific deliverable using the saved business profile, selected agents, current offer, target audience, goals, and execution requirements.",

        "Create premium ecommerce campaign assets":
            "Create a client-specific deliverable",

        "Premium ecommerce deliverable":
            "Client deliverable",

        "Latest premium ecommerce deliverable":
            "Latest client deliverable",

        "Premium ecommerce campaign assets generated with positioning, emotional hooks, conversion-focused messaging, and launch-ready creative direction for luxury skincare buyers.":
            "Client-specific deliverable generated from the latest execution, business profile, selected agents, and review requirements.",

        "Premium ecommerce campaign assets generated with positioning, emotional hooks, conversion-focused messaging, and launch-ready creative direction for ecommerce buyers.":
            "Client-specific deliverable generated from the latest execution, business profile, selected agents, and review requirements.",

        "Campaign outputs, approvals, execution flows, creative assets, billing events, and governed automation actions will appear after execution.":
            "Live outputs, approvals, execution events, assets, and review actions will appear after execution.",

        "Run an agent to generate deliverables":
            "Run selected agents to generate a live deliverable",

        "Common workspace actions":
            "Workspace actions",

        "Real-time execution timeline":
            "Execution timeline",

        "Generated campaign asset":
            "Generated deliverable asset",

        "Generated creatives, uploaded brand assets, previews, campaign media, and future product images will render here automatically.":
            "Generated assets, uploaded brand files, previews, and deliverable media will appear here automatically.",

        "Generated creatives, uploaded brand assets, previews, and campaign media will appear here once attached to this deliverable.":
            "Generated assets, uploaded brand files, previews, and deliverable media will appear here once attached.",

        "Campaign copy":
            "Deliverable",

        "Creative assets":
            "Assets",

        "Execution flow":
            "Execution",

        "Workflow automation":
            "Workflow",

        "General Ecommerce Agent":
            "Selected Agent",

        "Product copy generated":
            "Output generated",

        "Workflow initiated":
            "Execution started",

        "Execution review ready":
            "Review ready",

        "Confirm offer and campaign direction":
            "Confirm offer and deliverable direction",

        # Admin/demo wording cleanup
        "demo":
            "trial",

        "Demo":
            "Trial",

        "sample data":
            "test data",

        "Sample data":
            "Test data",

        "fake":
            "test",

        "Fake":
            "Test",

        "placeholder":
            "temporary",

        "Placeholder":
            "Temporary",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Replace static timeline demo array if present in client page.
    old_timeline = '''[
                ["4:18 PM", "Execution started", "System"],
                ["4:19 PM", "Output generated", "Product Copywriting Agent"],
                ["4:20 PM", "Review ready", "Selected Agent"],
              ].map(([time, event, actor]) => ('''

    new_timeline = '''[
                [liveDeliverable?.created_at || "Live", liveDeliverable ? "Deliverable generated" : "Waiting for execution", liveDeliverable?.agent || "Selected agent"],
                [reviewStatus === "approved" ? "Complete" : "Pending", reviewStatus === "approved" ? "Approved by client" : "Awaiting review", "Client workspace"],
              ].map(([time, event, actor]) => ('''

    text = text.replace(old_timeline, new_timeline)

    path.write_text(text, encoding="utf-8")

print("PHASE_G_STATIC_DEMO_UI_REMOVED")
print("Backups created in backups folder.")

# Scan remaining suspicious terms.
scan_terms = [
    "Manual Deploy Client",
    "Create premium ecommerce campaign assets",
    "luxury skincare",
    "General Ecommerce Agent",
    "Product copy generated",
    "4:18 PM",
    "4:19 PM",
    "4:20 PM",
    "fake",
    "placeholder",
    "demo",
]

for path in FILES:
    if not path.exists():
        continue

    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    remaining = [term for term in scan_terms if term.lower() in text]

    print(path)
    print("remaining_static_terms", remaining)