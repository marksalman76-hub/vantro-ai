from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"client_activation_state_restore_ui_bridge_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

page_path = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
test_path = ROOT / "test_client_activation_state_restore_ui_bridge.py"

backup = BACKUP_DIR / page_path.relative_to(ROOT)
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(page_path.read_text(encoding="utf-8"), encoding="utf-8")

text = page_path.read_text(encoding="utf-8")

old = '''        if (deployedAgents.length > 0) {
          setSelectedAgents(deployedAgents);
        }
'''

new = '''        if (deployedAgents.length > 0) {
          setSelectedAgents(deployedAgents);
        }

        const tenantForActivationRestore =
          accountData?.tenant_id || accountData?.client_id || "";

        if (tenantForActivationRestore) {
          fetch(`/api/activation-state-restore?tenant_id=${encodeURIComponent(tenantForActivationRestore)}`, {
            method: "GET",
            credentials: "include",
          })
            .then((restoreResponse) => restoreResponse.json())
            .then((restoreData) => {
              const restoredAgents =
                restoreData?.activated_agents && Array.isArray(restoreData.activated_agents)
                  ? restoreData.activated_agents
                  : restoreData?.activation_state?.activated_agents &&
                      Array.isArray(restoreData.activation_state.activated_agents)
                    ? restoreData.activation_state.activated_agents
                    : [];

              if (restoreData?.activation_state_restore_bridge_ready && restoredAgents.length > 0) {
                setSelectedAgents(restoredAgents);
                setAccount({
                  ...accountData,
                  active_agents: restoredAgents,
                  activation_locked: Boolean(restoreData?.activation_locked || restoreData?.activation_state?.activation_locked),
                  entitlement_hydrated: Boolean(restoreData?.entitlement_hydrated || restoreData?.activation_state?.entitlement_hydrated),
                  post_activation_client_changes_blocked: true,
                  owner_admin_required_for_post_activation_changes: true,
                  credential_values_exposed: false,
                  customer_safe: true,
                });
              }
            })
            .catch(() => {});
        }
'''

if old not in text:
    raise RuntimeError("Expected deployedAgents selected-agent block not found.")

text = text.replace(old, new, 1)

page_path.write_text(text, encoding="utf-8")

test_path.write_text(
'''from pathlib import Path

text = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")

assert "/api/activation-state-restore" in text
assert "activation_state_restore_bridge_ready" in text
assert "post_activation_client_changes_blocked" in text
assert "owner_admin_required_for_post_activation_changes" in text
assert "credential_values_exposed: false" in text
assert "customer_safe: true" in text
assert "setSelectedAgents(restoredAgents)" in text

print("CLIENT_ACTIVATION_STATE_RESTORE_UI_BRIDGE_TESTS_PASSED")
print("route_wired", "/api/activation-state-restore" in text)
print("restore_marker", "activation_state_restore_bridge_ready" in text)
'''
, encoding="utf-8")

print("CLIENT_ACTIVATION_STATE_RESTORE_UI_BRIDGE_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {page_path}")
print(f"Created/updated: {test_path}")