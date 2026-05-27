
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
