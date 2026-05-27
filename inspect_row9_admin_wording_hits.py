import os
import urllib.request

BASE = os.environ.get("FRONTEND_BASE_URL", "https://app.trance-formation.com.au").rstrip("/")
url = BASE + "/admin"

terms = [
    "internal prompt",
    "secret",
]

req = urllib.request.Request(
    url,
    headers={
        "User-Agent": "Row9AdminWordingInspector/1.0",
        "Accept": "text/html,*/*",
    },
    method="GET",
)

with urllib.request.urlopen(req, timeout=25) as response:
    body = response.read().decode("utf-8", errors="ignore")

print("STATUS_OK")
print("LEN", len(body))

lower = body.lower()

for term in terms:
    print("\n" + "=" * 80)
    print("TERM:", term)
    print("=" * 80)

    start = 0
    count = 0

    while True:
        idx = lower.find(term.lower(), start)
        if idx == -1:
            break

        count += 1
        a = max(0, idx - 500)
        b = min(len(body), idx + 900)
        print(f"\n--- MATCH {count} ---")
        print(body[a:b])

        start = idx + len(term)

    if count == 0:
        print("NO MATCHES")