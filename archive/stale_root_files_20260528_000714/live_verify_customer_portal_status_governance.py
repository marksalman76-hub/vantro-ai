import os
import json
import urllib.request
import urllib.error
import re
from urllib.parse import urljoin

BASE = os.getenv("FRONTEND_BASE_URL") or "https://app.trance-formation.com.au"

ROUTES = {
    "/client": [
        "ACTIVE",
        "INACTIVE",
        "Agent selections are locked after activation",
        "owner/admin approval",
        "Business Profile",
        "Integrations",
        "Billing",
        "Support",
    ],
}

FORBIDDEN = [
    "provider internals",
    "queue internals",
    "raw JSON",
    "debug route",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "ADMIN_PLATFORM_TOKEN",
]

def fetch(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "live-customer-portal-verify/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except Exception as e:
        return 0, str(e)

def chunk_urls(html):
    refs = set(re.findall(r'src="([^"]*?_next/static/[^"]+?\.js[^"]*)"', html))
    refs |= set(re.findall(r'href="([^"]*?_next/static/[^"]+?\.js[^"]*)"', html))
    return [urljoin(BASE.rstrip("/") + "/", r) for r in refs]

results = {}
failures = []
forbidden_hits = []

for route, markers in ROUTES.items():
    status, html = fetch(BASE.rstrip("/") + route)

    combined = html

    chunks = chunk_urls(html)

    for chunk in chunks[:80]:
        cs, ct = fetch(chunk)
        if cs == 200:
            combined += "\n" + ct

    marker_results = {}
    missing = []

    for marker in markers:
        present = marker in combined
        marker_results[marker] = present
        if not present:
            missing.append(marker)
            failures.append(f"{route} missing marker: {marker}")

    route_forbidden = []

    lowered = combined.lower()

    for forbidden in FORBIDDEN:
        if forbidden.lower() in lowered:
            route_forbidden.append(forbidden)
            forbidden_hits.append({
                "route": route,
                "marker": forbidden,
            })

    results[route] = {
        "status": status,
        "chunk_count_checked": len(chunks[:80]),
        "markers": marker_results,
        "missing": missing,
        "forbidden_hits": route_forbidden,
    }

    if status != 200:
        failures.append(f"{route} returned status {status}")

print(json.dumps({
    "frontend_base_url": BASE,
    "results": results,
    "credential_values_exposed": bool(forbidden_hits),
    "forbidden_hits": forbidden_hits,
}, indent=2))

if forbidden_hits:
    print("LIVE_CUSTOMER_PORTAL_VERIFY_FAILED")
    print("credential_values_exposed", True)
    raise SystemExit(1)

if failures:
    print("LIVE_CUSTOMER_PORTAL_VERIFY_FAILED")
    for failure in failures:
        print("-", failure)
    raise SystemExit(1)

print("LIVE_CUSTOMER_PORTAL_VERIFY_PASSED")
print("customer_portal_live", True)
print("active_inactive_status_live", True)
print("selection_lock_notice_live", True)
print("credential_values_exposed", False)