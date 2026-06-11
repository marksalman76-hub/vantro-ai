from pathlib import Path
from datetime import datetime
import subprocess

ROOT = Path(__file__).resolve().parent
CLIENT_PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
PANEL = ROOT / "frontend" / "src" / "components" / "DirectMediaProviderPanel.tsx"
TEST = ROOT / "test_admin_only_provider_diagnostics_panel.py"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"fix_admin_provider_diagnostics_client_build_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

for path in [CLIENT_PAGE, PANEL, TEST]:
    if path.exists():
        backup_name = str(path.relative_to(ROOT)).replace("\\", "__").replace("/", "__")
        (BACKUP_DIR / backup_name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

# Restore the client page from the last good commit before the broken diagnostics commit.
client_good = subprocess.check_output(
    ["git", "show", "56bd67a:frontend/src/app/client/page.tsx"],
    cwd=ROOT,
    text=True,
    encoding="utf-8",
    errors="replace",
)

client_lines = client_good.splitlines()
clean_client_lines = []
skip_component = False

for line in client_lines:
    stripped = line.strip()

    # Remove import only.
    if "DirectMediaProviderPanel" in line and "import" in line:
        continue

    # Remove JSX component only, including multiline props.
    if "<DirectMediaProviderPanel" in line:
        skip_component = True
        continue

    if skip_component:
        if "/>" in line or "</DirectMediaProviderPanel>" in line:
            skip_component = False
        continue

    clean_client_lines.append(line)

client = "\n".join(clean_client_lines) + "\n"

if "CLIENT_PORTAL_RUN_AGENT_ONLY_NO_PROVIDER_DIAGNOSTICS_V1" not in client:
    marker = (
        "\n      {/* CLIENT_PORTAL_RUN_AGENT_ONLY_NO_PROVIDER_DIAGNOSTICS_V1: "
        "Direct provider diagnostics are intentionally not rendered in the client portal. "
        "Clients use Run Agent Task only. */}\n"
    )

    # Put the marker just before closing </main> if possible.
    if "\n    </main>" in client:
        client = client.replace("\n    </main>", marker + "\n    </main>", 1)
    else:
        client += marker

CLIENT_PAGE.write_text(client, encoding="utf-8")

panel = PANEL.read_text(encoding="utf-8")

# Make diagnostics explicitly admin-only and testable without risky JSX surgery.
if "ADMIN_ONLY_PROVIDER_DIAGNOSTICS_PANEL_V1" not in panel:
    panel = "/* ADMIN_ONLY_PROVIDER_DIAGNOSTICS_PANEL_V1 */\n" + panel

panel = panel.replace("Generate media with selected software", "Advanced provider diagnostics")
panel = panel.replace("Expand panel", "Open diagnostics")
panel = panel.replace("Compact panel", "Hide diagnostics")

if "Admin-only provider testing" not in panel:
    panel = panel.replace(
        "Direct provider generation for video, audio, avatars and generated media. Admin/owner controls remain unrestricted.",
        "Admin-only provider testing for Runway, Kling, ElevenLabs, HeyGen, Replicate, OpenAI and Sync. Normal client workflows should use Run Agent Task.",
    )

if "if (!isAdmin) return null;" not in panel:
    panel = panel.replace(
        "if (!status && !isAdmin) return null;",
        "if (!isAdmin) return null;\n  if (!status && !isAdmin) return null;",
        1,
    )

PANEL.write_text(panel, encoding="utf-8")

TEST.write_text(
    r'''from pathlib import Path


def test_admin_only_provider_diagnostics_panel():
    panel = Path("frontend/src/components/DirectMediaProviderPanel.tsx").read_text(encoding="utf-8")
    assert "ADMIN_ONLY_PROVIDER_DIAGNOSTICS_PANEL_V1" in panel, "admin-only diagnostics marker missing"
    assert "Advanced provider diagnostics" in panel, "diagnostics title missing"
    assert "Open diagnostics" in panel, "open diagnostics button text missing"
    assert "if (!isAdmin) return null" in panel, "panel must be admin-only"
    assert "Generate media with selected software" not in panel, "old provider workflow title should not remain"


def test_client_portal_provider_diagnostics_removed():
    client = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")
    assert "CLIENT_PORTAL_RUN_AGENT_ONLY_NO_PROVIDER_DIAGNOSTICS_V1" in client, "client removal marker missing"
    assert "DirectMediaProviderPanel" not in client.replace("Direct provider diagnostics are intentionally not rendered in the client portal", ""), "client portal should not render provider diagnostics"


if __name__ == "__main__":
    test_admin_only_provider_diagnostics_panel()
    test_client_portal_provider_diagnostics_removed()
    print("ADMIN_ONLY_PROVIDER_DIAGNOSTICS_CLIENT_BUILD_FIX_TEST_PASSED")
''',
    encoding="utf-8",
)

print("ADMIN_PROVIDER_DIAGNOSTICS_CLIENT_BUILD_FIXED")
print(f"Backup: {BACKUP_DIR}")
print(f"Restored and updated: {CLIENT_PAGE}")
print(f"Updated: {PANEL}")
print(f"Updated: {TEST}")