from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_output_real_results_only_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

replacements = [
    (
        '''{liveDeliverable?.title || "Live premium ecommerce launch campaign"}''',
        '''{liveDeliverable?.title || "No deliverable generated yet"}''',
    ),
    (
        '''{liveDeliverable?.summary ||
                    "A client-ready campaign deliverable has been generated for the selected ecommerce task, including positioning, offer framing, conversion messaging, and execution-ready campaign direction."}''',
        '''{liveDeliverable?.summary ||
                    "Run an agent to generate a real client deliverable. Results, summaries, and uploaded or generated media will appear here automatically."}''',
    ),
    (
        '''{liveDeliverable?.tags || ["Live output", getAgentDisplayName(selectedAgents[0] || "product_copywriting_agent"), "Approval required", "Client-ready"]}''',
        '''{liveDeliverable?.tags || (liveDeliverable ? ["Live output", getAgentDisplayName(selectedAgents[0] || "product_copywriting_agent"), "Approval required", "Client-ready"] : ["Awaiting real output"])}''',
    ),
]

changed = 0
for old, new in replacements:
    if old in src:
        src = src.replace(old, new, 1)
        changed += 1

if changed != len(replacements):
    raise SystemExit(f"ERROR: Applied {changed}/{len(replacements)} replacements. No safe write completed.")

PAGE.write_text(src, encoding="utf-8")

print("OUTPUT_VIEWER_REAL_RESULTS_ONLY_WIRED")
print(f"Backup: {backup}")
print("No mock title:", "Live premium ecommerce launch campaign" not in src)
print("No mock campaign summary:", "A client-ready campaign deliverable has been generated for the selected ecommerce task" not in src)
print("Empty output state installed:", "No deliverable generated yet" in src and "Run an agent to generate a real client deliverable" in src)
print("Awaiting real output tag:", "Awaiting real output" in src)
print("Left Activity locked:", "Execution snapshot" in src and "Review latest output" in src)
print("Enterprise modal preserved:", "showEnterpriseCatalogueModal" in src)
print("Right execution column locked:", src.count("Live execution flow") == 1 and src.count("Business profile applied") == 1 and src.count("Governed execution, every time.") == 1)
print("Old mutations:", src.count("applyHorizontalExecutionLayout") + src.count("applyPremiumExecutionSectionLayout"))