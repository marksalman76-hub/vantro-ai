import requests

BASE = "http://localhost:3000"

for plan in ["starter", "growth", "business", "enterprise"]:
    html = requests.get(f"{BASE}/signup?plan={plan}", timeout=20).text.lower()
    print(plan)
    print("  page_200:", "select your ai agents" in html or "choose your ai agents" in html or len(html) > 1000)
    print("  head_agent_visible:", "head agent" in html)
    print("  orchestration_visible:", "orchestration agent" in html)