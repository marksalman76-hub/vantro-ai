import json
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
FRONTEND = ROOT / "frontend"

results = []

def add(name, ok, detail=""):
    results.append({"check": name, "ok": bool(ok), "detail": detail})
    print(f"{name}: {'OK' if ok else 'FAILED'} {detail}")

def run_cmd(name, cmd, cwd):
    try:
        p = subprocess.run(cmd, cwd=cwd, shell=True, text=True, capture_output=True, timeout=90)
        add(name, p.returncode == 0, (p.stdout + p.stderr)[-500:].replace("\n", " "))
    except Exception as e:
        add(name, False, str(e))

def http_get(name, url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "launch-qa"})
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode("utf-8", errors="replace")
            add(name, 200 <= r.status < 500, f"status={r.status} body={body[:180]}")
    except Exception as e:
        add(name, False, str(e))

print("BATCH_C_COMMERCIAL_HARDENING_LAUNCH_QA")

run_cmd("frontend_build", "npm run build", FRONTEND)
run_cmd("frontend_client_page_exists", "dir src\\app\\client\\page.tsx", FRONTEND)
run_cmd("frontend_api_routes_exist", "dir src\\app\\api", FRONTEND)

backend_candidates = [
    ROOT / "backend" / "app",
    ROOT / "services" / "control_api",
]
for path in backend_candidates:
    add(f"backend_path_exists_{path.name}", path.exists(), str(path))

http_get("frontend_client_page_local", "http://localhost:3000/client")
http_get("client_me_api_local", "http://localhost:3000/api/client-me")
http_get("latest_deliverable_api_local", "http://localhost:3000/api/client-latest-deliverable")

ok_count = sum(1 for r in results if r["ok"])
fail_count = len(results) - ok_count

print("\nBATCH_C_RESULTS")
print(json.dumps({"ok": ok_count, "failed": fail_count, "results": results}, indent=2))

if fail_count:
    print("BATCH_C_HAS_WARNINGS_OR_FAILURES")
    sys.exit(1)

print("BATCH_C_LAUNCH_QA_OK")