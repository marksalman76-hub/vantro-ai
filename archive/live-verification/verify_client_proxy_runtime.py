from pathlib import Path
import re

ROOT = Path.cwd()
FRONTEND = ROOT / "frontend"

bad_patterns = [
    "ecommerce-ai-agent-platform-1.onrender.com",
    "api.trance-formation.com.au/api/client-me",
    "api.trance-formation.com.au/api/client-business-profile",
    "api.trance-formation.com.au/api/client-execution-matrix",
]

good_routes = [
    "src/app/api/client-me/route.ts",
    "src/app/api/client-business-profile/route.ts",
    "src/app/api/client-execution-matrix/route.ts",
    "src/app/api/run-agent/route.ts",
]

print("\n=== VERIFYING API ROUTES ===")
for route in good_routes:
    path = FRONTEND / route
    print(route, "OK" if path.exists() else "MISSING")

print("\n=== SCANNING FOR BAD DIRECT BACKEND CALLS ===")

found = False

for path in FRONTEND.rglob("*"):
    if path.suffix not in {".ts", ".tsx", ".js", ".jsx"}:
        continue

    try:
        text = path.read_text(encoding="utf-8")
    except:
        continue

    for pattern in bad_patterns:
        if pattern in text:
            found = True
            print(f"\nFOUND BAD CALL:")
            print(path)
            print(pattern)

if not found:
    print("NO BAD DIRECT CALLS FOUND")

print("\nVERIFICATION COMPLETE")