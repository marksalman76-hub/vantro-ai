import os
import json
import time
import urllib.error
import urllib.request
from dotenv import load_dotenv

load_dotenv()

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"
ORIGIN = "https://app.trance-formation.com.au"
token = os.getenv("ADMIN_PLATFORM_TOKEN") or os.getenv("ADMIN_AUTH_SECRET") or ""

payload = {
    "account_reference": "live_email_debug_" + str(int(time.time())),
    "company_name": "Ability Care Live Email Debug",
    "contact_email": "stallonzayya@gmail.com",
    "package": "Manual Unlimited",
    "active_agents": ["strategy_agent"],
    "unlimited_credits": True,
}

req = urllib.request.Request(
    BASE + "/admin/deployment-control/manual-deploy",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "Origin": ORIGIN,
        "Referer": ORIGIN + "/admin",
        "x-actor-role": "owner",
        "x-tenant-id": "owner",
        "x-admin-token": token,
        "Authorization": "Bearer " + token,
    },
    method="POST",
)

try:
    response = urllib.request.urlopen(req, timeout=60)
    data = json.loads(response.read().decode("utf-8", errors="ignore"))
    print("HTTP", response.status)
    print("success", data.get("success"))
    print("activation_email", json.dumps(data.get("activation_email"), indent=2))
except urllib.error.HTTPError as error:
    print("HTTP", error.code)
    print(error.read().decode("utf-8", errors="ignore")[:4000])