from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
FRONTEND = ROOT / "frontend"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = BACKUPS / f"proxy_source_cleanup_before_{stamp}"
backup_dir.mkdir(exist_ok=True)

bad = "https://ecommerce-ai-agent-platform-1.onrender.com"
good = "https://api.trance-formation.com.au"

changed = []

for path in (FRONTEND / "src").rglob("*"):
    if path.suffix not in {".ts", ".tsx", ".js", ".jsx"}:
        continue

    text = path.read_text(encoding="utf-8")
    if bad in text:
        dest = backup_dir / path.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")

        text = text.replace(bad, good)
        path.write_text(text, encoding="utf-8")
        changed.append(str(path))

next_dir = FRONTEND / ".next"
if next_dir.exists():
    shutil.rmtree(next_dir)

verify = ROOT / "verify_client_proxy_source_only.py"
verify.write_text(r'''
from pathlib import Path

ROOT = Path.cwd()
FRONTEND = ROOT / "frontend"
bad = "ecommerce-ai-agent-platform-1.onrender.com"

found = []

for path in (FRONTEND / "src").rglob("*"):
    if path.suffix not in {".ts", ".tsx", ".js", ".jsx"}:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    if bad in text:
        found.append(str(path))

required_routes = [
    "frontend/src/app/api/client-me/route.ts",
    "frontend/src/app/api/client-business-profile/route.ts",
    "frontend/src/app/api/client-execution-matrix/route.ts",
    "frontend/src/app/api/run-agent/route.ts",
]

missing = [p for p in required_routes if not (ROOT / p).exists()]

print("BAD_SOURCE_CALLS", len(found))
for item in found:
    print(item)

print("MISSING_REQUIRED_ROUTES", len(missing))
for item in missing:
    print(item)

if found or missing:
    raise SystemExit("CLIENT_PROXY_SOURCE_VERIFY_FAILED")

print("CLIENT_PROXY_SOURCE_VERIFY_OK")
''', encoding="utf-8")

print("PROXY_SOURCE_CLEANUP_COMPLETE")
print("Backup:", backup_dir)
print("Changed files:")
for item in changed:
    print("-", item)
print("Removed frontend/.next cache")
print("Created verify_client_proxy_source_only.py")