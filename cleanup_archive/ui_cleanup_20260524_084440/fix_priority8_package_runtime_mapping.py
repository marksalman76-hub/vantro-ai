from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()

TARGET = ROOT / "backend" / "app" / "core" / "saas_provisioning_runtime.py"

if not TARGET.exists():
    raise FileNotFoundError(TARGET)

BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = BACKUP_DIR / f"saas_provisioning_runtime_before_package_mapping_fix_{timestamp}.py"
backup.write_text(TARGET.read_text(encoding="utf-8"), encoding="utf-8")

text = TARGET.read_text(encoding="utf-8")

# ---------------------------------------------------------
# inject canonical package normaliser
# ---------------------------------------------------------

if "def normalise_package_id(" not in text:

    insertion = r'''

PACKAGE_AGENT_LIMITS = {
    "starter": 2,
    "growth": 5,
    "professional": 10,
    "enterprise": 999,
}

def normalise_package_id(value):
    if not value:
        return "starter"

    value = str(value).strip().lower()

    aliases = {
        "starter": "starter",
        "basic": "starter",

        "growth": "growth",
        "pro": "growth",
        "scale": "growth",

        "professional": "professional",
        "premium": "professional",

        "enterprise": "enterprise",
        "unlimited": "enterprise",
    }

    return aliases.get(value, "starter")


def enforce_agent_limit(package_id, agents):
    limit = PACKAGE_AGENT_LIMITS.get(package_id, 2)

    if limit >= 999:
        return list(dict.fromkeys(agents))

    return list(dict.fromkeys(agents))[:limit]

'''

    marker = "from datetime import"
    idx = text.find(marker)

    if idx == -1:
        raise RuntimeError("Could not find insertion marker")

    next_newline = text.find("\n", idx)
    text = text[:next_newline+1] + insertion + text[next_newline+1:]

# ---------------------------------------------------------
# replace hardcoded starter fallback logic
# ---------------------------------------------------------

patterns = [
    (
        r'package\s*=\s*["\']starter["\']',
        'package = normalise_package_id(body.get("package") or body.get("package_id") or body.get("plan"))'
    ),
]

for pattern, replacement in patterns:
    text = re.sub(pattern, replacement, text)

# safer direct replacements

text = text.replace(
    'agent_limit = 2',
    'agent_limit = PACKAGE_AGENT_LIMITS.get(package, 2)'
)

text = text.replace(
    'activated_agents = []',
    'activated_agents = enforce_agent_limit(package, selected_agents or requested_agents or [])'
)

text = text.replace(
    'requested_agents = []',
    'requested_agents = selected_agents or requested_agents or []'
)

TARGET.write_text(text, encoding="utf-8")

print("PRIORITY8_PACKAGE_RUNTIME_MAPPING_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {TARGET}")