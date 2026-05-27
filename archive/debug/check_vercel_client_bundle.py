import re
import requests

base = "https://ecommerce-ai-agent-platform.vercel.app"
html = requests.get(base + "/client", timeout=60).text

scripts = re.findall(r'(?:src|href)="([^"]+)"', html)
assets = [item for item in scripts if "_next/static" in item]

print("assets", len(assets))

found = False
for asset in assets:
    url = asset if asset.startswith("http") else base + asset
    try:
        body = requests.get(url, timeout=60).text
    except Exception:
        continue

    if "client/execution-events" in body or "Loading execution timeline" in body or "executionTimeline" in body:
        print("FOUND_IN", asset)
        found = True
        break

print("FOUND", found)