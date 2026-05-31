import json
import os
import re
import urllib.request
import urllib.error

BASE = os.environ.get("FRONTEND_BASE_URL", "https://app.trance-formation.com.au").rstrip("/")

PLANS = {
    "starter": {
        "max_selectable_agents": 3,
        "available_count": 26,
        "head_agent_available": False,
    },
    "growth": {
        "max_selectable_agents": 6,
        "available_count": 26,
        "head_agent_available": False,
    },
    "business": {
        "max_selectable_agents": 12,
        "available_count": 26,
        "head_agent_available": False,
    },
    "enterprise": {
        "max_selectable_agents": 27,
        "available_count": 27,
        "head_agent_available": True,
    },
}

REQUIRED_AGENT_KEYS = {
    "strategist_agent",
    "business_growth_partnerships_agent",
    "lead_generator_agent",
    "marketing_specialist_agent",
    "social_media_content_agent",
    "seo_agent",
    "email_reply_agent",
    "crm_agent",
    "sales_closer_agent",
    "workflow_automation_agent",
}

FORBIDDEN_LITERAL = [
    "OPENAI_API_KEY",
    "STRIPE_SECRET_KEY",
    "ADMIN_PLATFORM_TOKEN",
    "DATABASE_URL",
    "JWT_SECRET",
    "raw json",
    "traceback",
    "internal prompt",
    "system prompt",
    "developer message",
    "provider secret",
    "webhook secret",
]

FORBIDDEN_PATTERNS = [
    re.compile(r"\bsk_live_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\bsk_test_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\bwhsec_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\btenant_[a-z0-9]{6,}\b", re.I),
    re.compile(r"\bclient_[a-z0-9]{6,}\b", re.I),
]

def forbidden_hits(body):
    hits = []
    lower = body.lower()

    for item in FORBIDDEN_LITERAL:
        if item.lower() in lower:
            hits.append(item)

    for pattern in FORBIDDEN_PATTERNS:
        match = pattern.search(body)
        if match:
            hits.append(match.group(0))

    return sorted(set(hits))

def fetch_json(path):
    url = BASE + path
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Row7AgentCatalogueVerifier/1.0",
            "Accept": "application/json,text/html,*/*",
        },
        method="GET",
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
            "path": path,
            "status": "ERROR",
            "error": str(exc),
            "ok": False,
        }

    data = None
    json_error = None
    try:
        data = json.loads(body)
    except Exception as exc:
        json_error = str(exc)

    return {
        "path": path,
        "status": status,
        "content_type": headers.get("Content-Type") or headers.get("content-type", ""),
        "cache": headers.get("X-Vercel-Cache") or headers.get("x-vercel-cache", ""),
        "matched_path": headers.get("X-Matched-Path") or headers.get("x-matched-path", ""),
        "body_sample": body[:800],
        "data": data,
        "json_error": json_error,
        "forbidden_hits": forbidden_hits(body),
    }

results = []
catalogue_errors = []

for plan, expected in PLANS.items():
    path = f"/api/signup-agent-selection/options/{plan}"
    result = fetch_json(path)
    data = result.get("data")
    errors = []

    if result.get("status") != 200:
        errors.append({"field": "status", "expected": 200, "actual": result.get("status")})

    if data is None:
        errors.append({"field": "json", "expected": "valid JSON", "actual": result.get("json_error")})
    else:
        for field, expected_value in expected.items():
            actual = data.get(field)
            if actual != expected_value:
                errors.append({"field": field, "expected": expected_value, "actual": actual})

        available_agents = data.get("available_agents") or []
        keys = {agent.get("key") for agent in available_agents if isinstance(agent, dict)}

        missing_required = sorted(REQUIRED_AGENT_KEYS - keys)
        if missing_required:
            errors.append({"field": "required_agent_keys", "missing": missing_required})

        head_agent_entries = [agent for agent in available_agents if isinstance(agent, dict) and agent.get("key") == "head_agent"]

        if plan != "enterprise" and head_agent_entries:
            errors.append({"field": "head_agent_visibility", "expected": "not selectable outside enterprise", "actual": "visible"})

        if plan == "enterprise" and not head_agent_entries:
            errors.append({"field": "head_agent_visibility", "expected": "visible for enterprise", "actual": "missing"})

        if data.get("credential_values_exposed") is not False:
            errors.append({
                "field": "credential_values_exposed",
                "expected": False,
                "actual": data.get("credential_values_exposed"),
            })

        if data.get("customer_safe") is not True:
            errors.append({
                "field": "customer_safe",
                "expected": True,
                "actual": data.get("customer_safe"),
            })

    result["catalogue_check"] = {
        "ok": not errors,
        "errors": errors,
    }

    results.append(result)

    if errors:
        catalogue_errors.append({"plan": plan, "errors": errors})

forbidden = [{"path": r["path"], "hits": r["forbidden_hits"]} for r in results if r.get("forbidden_hits")]

summary = {
    "frontend_base_url": BASE,
    "results": results,
    "forbidden_hits": forbidden,
    "catalogue_errors": catalogue_errors,
    "row7_agent_catalogue_ready": not forbidden and not catalogue_errors,
}

print(json.dumps(summary, indent=2))

if not summary["row7_agent_catalogue_ready"]:
    print("ROW7_AGENT_CATALOGUE_VERIFY_FAILED")
    raise SystemExit(1)

print("ROW7_AGENT_CATALOGUE_VERIFY_PASSED")