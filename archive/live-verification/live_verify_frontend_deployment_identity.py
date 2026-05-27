import requests

BASE = "https://trance-formation.com.au"

paths = [
    "/",
    "/signup",
    "/login",
    "/client",
    "/api/signup-agent-selection/options/starter",
    "/api/signup-agent-selection/options/enterprise",
]

for path in paths:
    url = BASE + path
    print("\n===", path, "===")
    try:
        r = requests.get(url, timeout=30)
        print("status", r.status_code)
        print("content_type", r.headers.get("content-type"))
        print("x-vercel-id", r.headers.get("x-vercel-id"))
        print("server", r.headers.get("server"))
        print(r.text[:500])
    except Exception as exc:
        print("ERROR", exc)

print("\nLIVE_FRONTEND_DEPLOYMENT_IDENTITY_CHECK_DONE")