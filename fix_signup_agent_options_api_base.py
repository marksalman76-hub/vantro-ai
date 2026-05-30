from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/api/signup-agent-selection/options/[plan]/route.ts")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups") / ("signup_agent_options_api_base_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "route.ts"
backup.write_text(text, encoding="utf-8")

old = '''function backendBase() {
  return process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";
}
'''

new = '''function backendBase() {
  return (
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    process.env.BACKEND_URL ||
    process.env.NEXT_PUBLIC_BACKEND_URL ||
    "https://api.trance-formation.com.au"
  );
}
'''

if old not in text:
    raise SystemExit("BACKEND_BASE_BLOCK_NOT_FOUND")

path.write_text(text.replace(old, new), encoding="utf-8")

print("SIGNUP_AGENT_OPTIONS_API_BASE_FIXED")
print("Backup:", backup)