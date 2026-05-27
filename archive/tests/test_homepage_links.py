import requests
import re

BASE = "http://localhost:3000"
html = requests.get(BASE, timeout=20).text

links = re.findall(r'href=["\']([^"\']+)["\']', html)

targets = [
    "/signup?plan=starter",
    "/signup?plan=growth",
    "/signup?plan=business",
    "/signup?plan=enterprise",
    "/agents",
]

print("FOUND_LINKS")
for target in targets:
    print(target, target in links)

print("RELEVANT_LINKS")
for link in links:
    lower = link.lower()
    if "signup" in lower or "agent" in lower or "enterprise" in lower:
        print(link)