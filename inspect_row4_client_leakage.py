import os
import urllib.request

BASE = os.environ.get("FRONTEND_BASE_URL", "https://app.trance-formation.com.au").rstrip("/")

TARGETS = [
    "/signup",
    "/api/signup-agent-selection/options/starter",
    "/api/signup-locked-activation/status",
]

for path in TARGETS:
    print("\n" + "=" * 80)
    print(path)
    print("=" * 80)

    url = BASE + path

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "LeakInspector/1.0"}
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        body = response.read().decode("utf-8", errors="ignore")

    lower = body.lower()

    idx = lower.find("client_")

    if idx == -1:
        print("NO client_ FOUND")
        continue

    start = max(0, idx - 500)
    end = min(len(body), idx + 1000)

    print(body[start:end])