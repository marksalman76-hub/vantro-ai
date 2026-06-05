from pathlib import Path

ROOT = Path.cwd()
ADMIN = ROOT / "frontend/src/app/admin/page.tsx"

text = ADMIN.read_text(encoding="utf-8")
original = text

# Ensure Operations Store exists in nav items.
if '"Operations Store"' not in text:
    text = text.replace(
        'const navItems = ["Overview", "Run Agent", "Deploy Clients", "Client Registry", "Runtime Health", "Provider Governance", "Orchestration", "Recovery", "Billing"];',
        'const navItems = ["Overview", "Run Agent", "Deploy Clients", "Client Registry", "Runtime Health", "Provider Governance", "Orchestration", "Recovery", "Billing", "Operations Store"];'
    )

# Ensure section map points to the real panel id.
if '"Operations Store": "admin-operations-store"' not in text:
    text = text.replace(
        '"Billing": "admin-billing",',
        '"Billing": "admin-billing",\n      "Operations Store": "admin-operations-store",'
    )

# Ensure the actual section has the matching id.
if 'id="admin-operations-store"' not in text:
    # If panel exists but wrapper id is missing, insert before the visible title.
    text = text.replace(
        '<Panel title="Operations Store"',
        '<div id="admin-operations-store">\n              <Panel title="Operations Store"',
        1
    )
    text = text.replace(
        '<div id="admin-billing">',
        '</div>\n\n            <div id="admin-billing">',
        1
    )

if text == original:
    print("NO_CHANGE_OPERATIONS_STORE_NAVIGATION_ALREADY_WIRED")
else:
    ADMIN.write_text(text, encoding="utf-8", newline="\n")
    print("OPERATIONS_STORE_SIDEBAR_NAVIGATION_FIXED")