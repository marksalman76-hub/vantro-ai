from pathlib import Path
import re

front_path = Path("frontend/src/app/client/page.tsx")
backend_paths = [
    Path("backend/app/agents/agent_registry.py"),
    Path("backend/app/core/global_agent_registry.py"),
    Path("backend/app/core/governance_execution_registry.py"),
]

front = front_path.read_text(encoding="utf-8", errors="ignore")

front_block_match = re.search(
    r"const\s+AGENT_DISPLAY_NAMES\s*:\s*Record<string,\s*string>\s*=\s*\{(?P<body>.*?)\};",
    front,
    flags=re.S,
)

if not front_block_match:
    raise RuntimeError("Could not find typed AGENT_DISPLAY_NAMES in client page.")

front_ids = sorted(set(re.findall(r"\b([a-z0-9_]+_agent)\s*:", front_block_match.group("body"))))

backend_text = ""
for path in backend_paths:
    if path.exists():
        backend_text += "\n" + path.read_text(encoding="utf-8", errors="ignore")

backend_ids = sorted(set(re.findall(r"['\"]([a-z0-9_]+_agent)['\"]", backend_text)))

missing_backend = [agent for agent in front_ids if agent not in backend_ids]
missing_front = [agent for agent in backend_ids if agent not in front_ids]

print("FRONT_COUNT", len(front_ids))
print("BACKEND_COUNT", len(backend_ids))

print("\nFRONT_NOT_IN_BACKEND")
if missing_backend:
    for agent in missing_backend:
        print("-", agent)
else:
    print("none")

print("\nBACKEND_NOT_IN_FRONT")
if missing_front:
    for agent in missing_front:
        print("-", agent)
else:
    print("none")

print("\nFRONT_IDS")
for agent in front_ids:
    print("-", agent)

if not missing_backend:
    print("\nALIGNMENT_STATUS FRONTEND_AGENTS_REGISTERED_IN_BACKEND")
else:
    print("\nALIGNMENT_STATUS MISSING_BACKEND_REGISTRATION")