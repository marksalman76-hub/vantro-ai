import requests

BASE = "https://app.trance-formation.com.au"

routes = [
    "/api/client-me",
    "/api/client-business-profile",
    "/api/client-execution-matrix",
    "/api/run-agent",
    "/client",
]

for route in routes:
    url = BASE + route
    try:
        r = requests.get(url, timeout=30)
        print(route, r.status_code, r.headers.get("content-type"))
        print(r.text[:300].replace("\n", " "))
        print("-" * 60)
    except Exception as e:
        print(route, "ERROR", e)