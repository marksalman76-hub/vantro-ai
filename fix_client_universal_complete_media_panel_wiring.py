from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
CLIENT_PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
COMPONENT = ROOT / "frontend" / "src" / "components" / "UniversalCompleteMediaRunAgentPanel.tsx"
TEST = ROOT / "test_client_universal_complete_media_run_agent_panel.py"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"fix_client_universal_complete_media_panel_wiring_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

for path in [CLIENT_PAGE, COMPONENT, TEST]:
    if path.exists():
        backup_name = str(path.relative_to(ROOT)).replace("\\", "__").replace("/", "__")
        (BACKUP_DIR / backup_name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

client = CLIENT_PAGE.read_text(encoding="utf-8")

if not COMPONENT.exists():
    raise SystemExit("MISSING_COMPONENT_UniversalCompleteMediaRunAgentPanel")

if "UniversalCompleteMediaRunAgentPanel" not in client:
    import_anchor = 'import LatestDeliverableViewer from "./LatestDeliverableViewer";'
    if import_anchor not in client:
        raise SystemExit("CLIENT_IMPORT_ANCHOR_NOT_FOUND")
    client = client.replace(
        import_anchor,
        import_anchor + '\nimport UniversalCompleteMediaRunAgentPanel from "@/components/UniversalCompleteMediaRunAgentPanel";',
        1,
    )

if "CLIENT_RUN_AGENT_UNIVERSAL_COMPLETE_MEDIA_PANEL_V1" not in client:
    possible_anchors = [
        '<h3 style={cardTitle}>Select agents and launch governed execution.</h3>',
        '<StepHeader number="01" title="Run AI Agent" />',
        'Run AI Agent',
    ]

    anchor = ""
    for candidate in possible_anchors:
        if candidate in client:
            anchor = candidate
            break

    if not anchor:
        raise SystemExit("NO_SAFE_RUN_AGENT_INSERTION_ANCHOR_FOUND")

    panel_block = '''
            {/* CLIENT_RUN_AGENT_UNIVERSAL_COMPLETE_MEDIA_PANEL_V1 */}
            <UniversalCompleteMediaRunAgentPanel
              selectedAgent={selectedAgents[0] || "social_media_manager_content_creator_agent"}
              businessProfile={businessProfile}
              onResult={(deliverable) => {
                setLiveDeliverable(deliverable as any);
                setSelectedAssetIndex(0);
                setExecutionState("completed");
                setToastMessage("Complete media file generated and ready for review.");
              }}
            />
'''

    if anchor == 'Run AI Agent':
        idx = client.find(anchor)
        line_start = client.rfind("\n", 0, idx)
        line_end = client.find("\n", idx)
        if line_end == -1:
            line_end = idx + len(anchor)
        client = client[:line_end + 1] + panel_block + client[line_end + 1:]
    else:
        client = client.replace(anchor, anchor + "\n" + panel_block, 1)

CLIENT_PAGE.write_text(client, encoding="utf-8")

TEST.write_text(
    r'''from pathlib import Path


def test_client_universal_complete_media_panel_installed():
    client = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")
    component = Path("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx").read_text(encoding="utf-8")

    assert "CLIENT_RUN_AGENT_UNIVERSAL_COMPLETE_MEDIA_PANEL_V1" in client, "client run agent marker missing"
    assert "UniversalCompleteMediaRunAgentPanel" in client, "client page does not import/render panel"
    assert "Complete media file" in component, "component title missing"
    assert "Create complete media file" in component, "generate button missing"
    assert "Age range" in component, "age control missing"
    assert "Gender presentation" in component, "gender control missing"
    assert "Ethnicity / cultural appearance" in component, "ethnicity/cultural appearance control missing"
    assert "Ultra-human likeness" in component, "avatar likeness control missing"
    assert "Facial features" in component, "facial feature control missing"
    assert "Expressions" in component, "expression control missing"
    assert "/api/universal-complete-media" in component, "client-safe universal complete media route missing"


def test_client_universal_complete_media_routes_exist():
    assert Path("frontend/src/app/api/universal-complete-media/route.ts").exists(), "complete media route missing"
    assert Path("frontend/src/app/api/universal-complete-media-status/route.ts").exists(), "status route missing"
    assert Path("frontend/src/app/api/universal-complete-media-asset/route.ts").exists(), "asset route missing"


if __name__ == "__main__":
    test_client_universal_complete_media_panel_installed()
    test_client_universal_complete_media_routes_exist()
    print("CLIENT_UNIVERSAL_COMPLETE_MEDIA_RUN_AGENT_PANEL_TEST_PASSED")
''',
    encoding="utf-8",
)

print("CLIENT_UNIVERSAL_COMPLETE_MEDIA_PANEL_WIRING_FIXED")
print(f"Backup: {BACKUP_DIR}")
print(f"Updated: {CLIENT_PAGE}")
print(f"Verified component exists: {COMPONENT}")
print(f"Created: {TEST}")