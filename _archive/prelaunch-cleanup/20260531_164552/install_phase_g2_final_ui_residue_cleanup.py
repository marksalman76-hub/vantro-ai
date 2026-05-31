from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"

for path in [client_page, admin_page]:
    if path.exists():
        backup = BACKUPS / f"{path.stem}_before_phase_g2_final_ui_residue_cleanup_{timestamp}{path.suffix}"
        backup.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

text = client_page.read_text(encoding="utf-8", errors="ignore")

replacements = {
    'master_orchestrator_agent: "Master Orchestrator Agent",\n': "",
    'general_ecommerce_agent: "Selected Agent",\n': "",
    "Run premium ecommerce AI agents, generate governed outputs, manage": "Run selected AI agents, generate governed outputs, manage",
    "ecommerce niche, product category, and market position": "business niche, product category, and market position",
    "campaigns, creative assets, copy, positioning, and execution recommendations.": "deliverables, assets, copy, positioning, and execution recommendations.",
    "Premium deliverables": "Client deliverables",
    "Premium deliverable": "Client deliverable",
    "premium deliverables": "client deliverables",
    "premium deliverable": "client deliverable",
    '"17 May 2026 ┬╖ 4:21 PM"': '"Ready for review"',
}

for old, new in replacements.items():
    text = text.replace(old, new)

old_status_cards = '''[
                ["Campaign drafted", "Done", "4:18 PM"],
                ["Review pending", "In progress", "4:19 PM"],
                ["Approval required", "Pending", "4:20 PM"],
              ].map(([item, status, time]) => ('''

new_status_cards = '''[
                ["Execution requested", executionState === "idle" ? "Waiting" : "Started", liveDeliverable?.created_at || "Live"],
                ["Deliverable status", executionState === "completed" ? "Ready" : "Pending", liveDeliverable?.created_at || "Live"],
                ["Client review", reviewStatus === "approved" ? "Approved" : reviewStatus === "rejected" ? "Revision requested" : "Pending", reviewStatus === "approved" ? "Complete" : "Open"],
              ].map(([item, status, time]) => ('''

text = text.replace(old_status_cards, new_status_cards)

client_page.write_text(text, encoding="utf-8")

# Admin page: remove remaining exact legacy label only, keep functional deployment controls.
admin_text = admin_page.read_text(encoding="utf-8", errors="ignore")
admin_text = admin_text.replace("Manual Deploy Client", "Create Client Workspace")
admin_page.write_text(admin_text, encoding="utf-8")

print("PHASE_G2_FINAL_UI_RESIDUE_CLEANUP_INSTALLED")
print("Backups created.")

scan_terms = [
    "master_orchestrator_agent",
    "general_ecommerce_agent",
    "Premium ecommerce",
    "premium ecommerce",
    "Create premium ecommerce",
    "luxury skincare",
    "General Ecommerce Agent",
    "Product copy generated",
    "4:18 PM",
    "4:19 PM",
    "4:20 PM",
    "17 May 2026",
    "Manual Deploy Client",
]

for path in [client_page, admin_page]:
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    remaining = [term for term in scan_terms if term.lower() in text]
    print(path)
    print("remaining_terms", remaining)