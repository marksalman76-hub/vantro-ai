from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS2_WORKSPACE_REBUILD_RESULTS")

checks = {
    "responsive_workspace_grid": "responsiveWorkspaceGridStyle" in text,
    "responsive_secondary_grid": "responsiveSecondaryGridStyle" in text,
    "workspace_controls_copy": "Workspace controls" in text,
    "activity_feed_copy": "Activity feed" in text,
    "execution_deliverables_copy": "Execution deliverables" in text,
    "agent_copy": "Purchased & active agents" in text,
    "premium_shadow": "0 20px 55px rgba(15,23,42,0.06)" in text,
    "governed_activity_copy": "Governed activity tracking connected" in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS2_WORKSPACE_REBUILD_OK")
