from pathlib import Path
from datetime import datetime

path = Path("backend/app/main.py")
lines = path.read_text(encoding="utf-8").splitlines()

backup_dir = Path("backups") / ("stripe_checkout_response_extraction_line_based_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "main.py"
backup.write_text("\n".join(lines) + "\n", encoding="utf-8")

start = None
end = None

for i, line in enumerate(lines):
    if line.strip() == "session_id = None":
        start = i
        break

if start is None:
    raise SystemExit("SESSION_ID_START_NOT_FOUND")

for i in range(start, min(start + 80, len(lines))):
    if lines[i].strip().startswith("if not checkout_url:"):
        for j in range(i + 1, min(i + 20, len(lines))):
            if lines[j].strip() == "pass":
                end = j + 1
                break
        break

if end is None:
    raise SystemExit("CHECKOUT_URL_BLOCK_END_NOT_FOUND")

replacement = [
    "        session_payload = {}",
    "",
    "        try:",
    "            session_payload = dict(session)",
    "        except Exception:",
    "            session_payload = {}",
    "",
    "        if not session_payload:",
    "            try:",
    "                session_payload = session.to_dict_recursive()",
    "            except Exception:",
    "                session_payload = {}",
    "",
    "        if not session_payload:",
    "            try:",
    "                session_payload = session.to_dict()",
    "            except Exception:",
    "                session_payload = {}",
    "",
    "        session_id = (",
    "            session_payload.get(\"id\")",
    "            or getattr(session, \"id\", None)",
    "        )",
    "",
    "        checkout_url = (",
    "            session_payload.get(\"url\")",
    "            or getattr(session, \"url\", None)",
    "        )",
]

updated = lines[:start] + replacement + lines[end:]
path.write_text("\n".join(updated) + "\n", encoding="utf-8")

print("STRIPE_CHECKOUT_RESPONSE_EXTRACTION_LINE_BASED_FIXED")
print("Backup:", backup)
print("Replaced lines:", start + 1, "to", end)