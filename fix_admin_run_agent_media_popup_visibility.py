from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent

COMPONENT = ROOT / "frontend" / "src" / "components" / "UniversalCompleteMediaRunAgentPanel.tsx"
TEST = ROOT / "test_admin_run_agent_media_popup_visibility.py"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"admin_run_agent_media_popup_visibility_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

for path in [COMPONENT, TEST]:
    if path.exists():
        backup_name = str(path.relative_to(ROOT)).replace("\\", "__").replace("/", "__")
        (BACKUP_DIR / backup_name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

component = COMPONENT.read_text(encoding="utf-8")

if "ADMIN_MEDIA_POPUP_ALWAYS_VISIBLE_FOR_SELECTED_AGENT_V1" not in component:
    component = component.replace(
        '''  const activeAgents = selectedAgents?.length ? selectedAgents : selectedAgent ? [selectedAgent] : [];
  const mediaCapable = activeAgents.some(isCreativeCapableAgent);''',
        '''  const activeAgents = selectedAgents?.length ? selectedAgents : selectedAgent ? [selectedAgent] : [];

  // ADMIN_MEDIA_POPUP_ALWAYS_VISIBLE_FOR_SELECTED_AGENT_V1
  // Admin can see the media options whenever an agent is selected. Client remains creative-agent gated.
  const mediaCapable = mode === "admin"
    ? activeAgents.length > 0
    : activeAgents.some(isCreativeCapableAgent);''',
        1,
    )

    component = component.replace(
        '''  const statusText = enabled ? "Complete media enabled" : "Optional media output";''',
        '''  const selectedAgentLooksCreative = activeAgents.some(isCreativeCapableAgent);
  const statusText = enabled
    ? "Complete media enabled"
    : mode === "admin" && !selectedAgentLooksCreative
    ? "Admin override available"
    : "Optional media output";''',
        1,
    )

COMPONENT.write_text(component, encoding="utf-8")

TEST.write_text(
    r'''from pathlib import Path


def test_admin_media_popup_visible_for_selected_agent():
    component = Path("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx").read_text(encoding="utf-8")

    assert "ADMIN_MEDIA_POPUP_ALWAYS_VISIBLE_FOR_SELECTED_AGENT_V1" in component, "admin visibility override marker missing"
    assert 'mode === "admin"' in component, "admin mode condition missing"
    assert "activeAgents.length > 0" in component, "admin popup must show when any agent is selected"
    assert ": activeAgents.some(isCreativeCapableAgent)" in component, "client creative-agent gate must remain"
    assert 'data-run-agent-media-popup="true"' in component, "media popup marker missing"
    assert "Create complete media when Run Agent is clicked" in component, "popup Run Agent wording missing"


if __name__ == "__main__":
    test_admin_media_popup_visible_for_selected_agent()
    print("ADMIN_RUN_AGENT_MEDIA_POPUP_VISIBILITY_TEST_PASSED")
''',
    encoding="utf-8",
)

print("ADMIN_RUN_AGENT_MEDIA_POPUP_VISIBILITY_FIXED")
print(f"Backup: {BACKUP_DIR}")
print(f"Updated: {COMPONENT}")
print(f"Created: {TEST}")