import requests

BASE = "https://trance-formation.com.au"

checks = [
    ("signup_page", "GET", f"{BASE}/signup", None),
    ("starter_options", "GET", f"{BASE}/api/signup-agent-selection/options/starter", None),
    ("enterprise_options", "GET", f"{BASE}/api/signup-agent-selection/options/enterprise", None),
    ("validate_selection", "POST", f"{BASE}/api/signup-agent-selection/validate", {
        "plan": "starter",
        "selected_agent_keys": ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
    }),
    ("activation_packet", "POST", f"{BASE}/api/signup-agent-selection/activation-packet", {
        "plan": "starter",
        "selected_agent_keys": ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
    }),
]

for name, method, url, payload in checks:
    if method == "GET":
        r = requests.get(url, timeout=30)
    else:
        r = requests.post(url, json=payload, timeout=30)

    print("\n===", name, "===")
    print("status", r.status_code)
    print("content_type", r.headers.get("content-type"))

    text = r.text[:800]
    print(text)

    if r.status_code >= 400:
        raise SystemExit(f"{name} failed with {r.status_code}")

print("\nLIVE_SIGNUP_AGENT_SELECTION_UI_TEST_PASSED")