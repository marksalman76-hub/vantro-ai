import os, re, json, urllib.request, urllib.error
from urllib.parse import urljoin

BASE = os.getenv("FRONTEND_BASE_URL") or "https://ecommerce-ai-agent-platform-d04qm32ds.vercel.app"

ROUTES = {
    "/admin": ["Admin Command Centre", "Owner Control Plane", "Readiness Panel", "Owner Governance Rules"],
    "/admin/provider-execution": ["Provider Execution Dashboard", "Provider Job Detail", "Execution Timeline", "Governed Actions"],
}

FORBIDDEN = ["sk-", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET", "ADMIN_PLATFORM_TOKEN"]

def fetch(path):
    url = path if path.startswith("http") else BASE.rstrip("/") + path
    req = urllib.request.Request(url, headers={"User-Agent": "runtime-aware-admin-verify/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except Exception as e:
        return 0, str(e)

def chunks_from_html(html):
    refs = set(re.findall(r'src="([^"]*?_next/static/[^"]+?\.js[^"]*)"', html))
    refs |= set(re.findall(r'href="([^"]*?_next/static/[^"]+?\.js[^"]*)"', html))
    return [urljoin(BASE.rstrip("/") + "/", r) for r in refs]

results = {}
failures = []
secret_hits = []

for route, markers in ROUTES.items():
    status, html = fetch(route)
    combined = html
    chunk_urls = chunks_from_html(html)

    for chunk in chunk_urls[:80]:
        cs, ct = fetch(chunk)
        if cs == 200:
            combined += "\n" + ct

    marker_results = {m: (m in combined) for m in markers}
    missing = [m for m, ok in marker_results.items() if not ok]

    for forbidden in FORBIDDEN:
        if forbidden in combined:
            secret_hits.append({"route": route, "marker": forbidden})

    results[route] = {
        "status": status,
        "chunk_count_checked": len(chunk_urls[:80]),
        "markers": marker_results,
        "missing": missing,
    }

    if status != 200:
        failures.append(f"{route} returned {status}")
    for m in missing:
        failures.append(f"{route} missing marker after HTML+chunk scan: {m}")

print(json.dumps({
    "frontend_base_url": BASE,
    "results": results,
    "credential_values_exposed": bool(secret_hits),
    "secret_hits": secret_hits,
}, indent=2))

if secret_hits:
    print("LIVE_ADMIN_OWNER_CONTROL_PLANE_RUNTIME_AWARE_VERIFY_FAILED")
    print("credential_values_exposed", True)
    raise SystemExit(1)

if failures:
    print("LIVE_ADMIN_OWNER_CONTROL_PLANE_RUNTIME_AWARE_VERIFY_FAILED")
    for f in failures:
        print("-", f)
    raise SystemExit(1)

print("LIVE_ADMIN_OWNER_CONTROL_PLANE_RUNTIME_AWARE_VERIFY_PASSED")
print("admin_command_centre_live", True)
print("provider_execution_runtime_ui_live", True)
print("credential_values_exposed", False)