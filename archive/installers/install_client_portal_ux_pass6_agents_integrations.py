from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_ux_pass6_agents_integrations_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
original = text
backup.write_text(original, encoding="utf-8")

# 1) Add safe local/default agent options when account active_agents are not loaded.
text = text.replace(
    "const DEFAULT_AGENTS: string[] = [];",
    '''const DEFAULT_AGENTS: string[] = [
  "product_research_agent",
  "product_copywriting_agent",
  "ugc_creative_agent",
  "product_image_agent",
  "crm_ai_agent",
];'''
)

# 2) Improve run-agent selector layout and card styling.
text = text.replace(
    'gridTemplateColumns: "320px minmax(0,1fr)"',
    'gridTemplateColumns: "minmax(300px, 0.92fr) minmax(360px, 1.08fr)"'
)

text = text.replace(
    'border: active ? "1px solid #93c5fd" : "1px solid #e5eaf2"',
    'border: active ? "1px solid rgba(37, 99, 235, 0.38)" : "1px solid rgba(15, 23, 42, 0.10)"'
)

text = text.replace(
    'padding: "14px 16px"',
    'padding: "13px 14px"'
)

# 3) Clean harsh/black textarea borders in the client page.
text = text.replace(
    'border: "1px solid black"',
    'border: "1px solid rgba(15, 23, 42, 0.12)"'
)

text = text.replace(
    'border: "2px solid black"',
    'border: "1px solid rgba(15, 23, 42, 0.12)"'
)

text = text.replace(
    'borderRadius: 999,',
    'borderRadius: 16,'
)

# 4) Make run task textarea more premium.
text = text.replace(
    'rows={7}',
    'rows={6}'
)

text = text.replace(
    'resize: "none",\n                    borderRadius: 18,',
    'resize: "none",\n                    borderRadius: 18,\n                    boxShadow: "inset 0 1px 2px rgba(15, 23, 42, 0.04)",'
)

# 5) Convert integration cards toward compact pill-like rows.
text = text.replace(
    'gridTemplateColumns: "repeat(auto-fit,minmax(280px,1fr))"',
    'gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))"'
)

text = text.replace(
    'Used by: {integration.used_by_agents.slice(0, 3).join(", ")}',
    'Used by active agents'
)

text = text.replace(
    'Providers: {integration.providers.slice(0, 4).join(", ")}',
    'Provider ready'
)

text = text.replace(
    'Access: {integration.recommended_auth}',
    'Secure connection'
)

# 6) Hide some integration detail lines visually by making them compact.
text = text.replace(
    'fontSize: 12, lineHeight: 1.55',
    'fontSize: 11.5, lineHeight: 1.35'
)

# 7) Add marker.
if "client_portal_ux_pass6_agents_integrations" not in text:
    text = text.replace(
        "// client_portal_ux_pass5_premium_inputs",
        "// client_portal_ux_pass5_premium_inputs\n// client_portal_ux_pass6_agents_integrations"
    )

if text == original:
    raise RuntimeError("No Pass 6 changes applied.")

PAGE.write_text(text, encoding="utf-8")

TEST = ROOT / "test_client_portal_ux_pass6_agents_integrations.py"
TEST.write_text(r'''
from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS6_AGENTS_INTEGRATIONS_RESULTS")

checks = {
    "marker": "client_portal_ux_pass6_agents_integrations" in text,
    "default_agents_added": '"product_copywriting_agent"' in text and '"crm_ai_agent"' in text,
    "agent_grid_fixed": 'gridTemplateColumns: "minmax(300px, 0.92fr) minmax(360px, 1.08fr)"' in text,
    "integration_pill_grid": 'gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))"' in text,
    "no_black_border": 'border: "1px solid black"' not in text and 'border: "2px solid black"' not in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS6_AGENTS_INTEGRATIONS_OK")
'''.lstrip(), encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS6_AGENTS_INTEGRATIONS_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print(f"Created: {TEST}")