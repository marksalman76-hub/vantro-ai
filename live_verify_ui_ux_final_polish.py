import json
import os
import urllib.request
import urllib.error

FRONTEND = os.environ.get("FRONTEND_BASE_URL", "https://app.trance-formation.com.au").rstrip("/")

ROUTES = [
    "/",
    "/signup",
    "/activate",
    "/login",
    "/client",
    "/client/billing",
    "/admin",
]

REQUIRED_MARKERS = {
    "/": [
        "Ecommerce AI Agent Platform",
    ],
    "/signup": [
        "Ecommerce AI Agent Platform",
    ],
    "/activate": [
        "activation",
    ],
    "/client": [
        "ACTIVE",
        "INACTIVE",
        "Business Profile",
        "Integrations",
        "Support",
        "Agent selections are locked after activation",
        "owner/admin approval",
    ],
    "/client/billing": [
        "billing",
    ],
    "/admin": [
        "Readiness",
    ],
}

FORBIDDEN_UI = [
    "traceback",
    "stack trace",
    "internal prompt",
    "system prompt",
    "developer message",
    "raw json",
    "[object Object]",
]

def fetch(route):
    url = FRONTEND + route + "?row12=ui-ux-final-polish"

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Row12UIUXPolishVerifier/1.0",
            "Accept": "text/html,*/*",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            body = response.read().decode("utf-8", errors="ignore")
            status = response.status
            headers = dict(response.headers)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        status = exc.code
        headers = dict(exc.headers)
    except Exception as exc:
        return {
            "route": route,
            "status": "ERROR",
            "error": str(exc),
        }

    lower = body.lower()

    required = REQUIRED_MARKERS.get(route, [])
    markers = {marker: marker.lower() in lower for marker in required}

    forbidden_hits = [item for item in FORBIDDEN_UI if item.lower() in lower]

    return {
        "route": route,
        "status": status,
        "content_type": headers.get("Content-Type") or headers.get("content-type", ""),
        "cache": headers.get("X-Vercel-Cache") or headers.get("x-vercel-cache", ""),
        "matched_path": headers.get("X-Matched-Path") or headers.get("x-matched-path", ""),
        "markers": markers,
        "markers_ok": all(markers.values()) if markers else True,
        "forbidden_hits": forbidden_hits,
        "body_sample": body[:1200],
    }

results = [fetch(route) for route in ROUTES]

status_failures = [r for r in results if r.get("status") not in [200, 401, 403]]
marker_failures = [r for r in results if not r.get("markers_ok", True)]
forbidden = [r for r in results if r.get("forbidden_hits")]

summary = {
    "frontend_base_url": FRONTEND,
    "results": results,
    "status_failures": status_failures,
    "marker_failures": marker_failures,
    "forbidden_hits": forbidden,
    "row12_ui_ux_final_polish_ready": (
        not status_failures
        and not marker_failures
        and not forbidden
    ),
}

print(json.dumps(summary, indent=2))

if not summary["row12_ui_ux_final_polish_ready"]:
    print("ROW12_UI_UX_FINAL_POLISH_VERIFY_FAILED")
    raise SystemExit(1)

print("ROW12_UI_UX_FINAL_POLISH_VERIFY_PASSED")