import json
import urllib.request

url = "https://app.trance-formation.com.au/api/delegated-workforce-execution"

payload = {
    "implementation_plan": {
        "action_packets": [
            {
                "packet_id": "norm_live_001",
                "recommended_agent": "marketing_specialist_agent",
                "title": "4. Execution plan with concrete steps",
                "risk_level": "medium",
                "approval_required": False,
            },
            {
                "packet_id": "norm_live_002",
                "recommended_agent": "marketing_specialist_agent",
                "title": "b. Capability building and strategic partnerships",
                "risk_level": "medium",
                "approval_required": False,
            },
            {
                "packet_id": "norm_live_003",
                "recommended_agent": "marketing_specialist_agent",
                "title": "Launch paid campaign and increase budget",
                "risk_level": "medium",
                "approval_required": False,
            },
        ]
    },
    "owner_approved": False,
    "client_owned_agents": ["marketing_specialist_agent"],
    "package_tier": "enterprise",
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=60) as response:
        body = response.read().decode("utf-8")
        print("HTTP_STATUS", response.status)
        print(body)
except Exception as e:
    print("REQUEST_FAILED", repr(e))
    if hasattr(e, "read"):
        print(e.read().decode("utf-8", errors="replace"))