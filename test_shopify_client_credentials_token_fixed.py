import getpass
import requests

shop = "ncn1m2-ch.myshopify.com"

client_id = input("Paste Shopify Client ID only: ").strip()
client_secret = getpass.getpass("Paste Shopify Client Secret only: ").strip()

url = f"https://{shop}/admin/oauth/access_token"

response = requests.post(
    url,
    data={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    },
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    timeout=60,
)

print("HTTP", response.status_code)

try:
    data = response.json()
except Exception:
    print(response.text)
    raise SystemExit

if response.ok:
    token = data.get("access_token", "")
    print("TOKEN_RECEIVED", bool(token))
    print("TOKEN_PREFIX", token[:6])
    print("SCOPE", data.get("scope"))
    print("EXPIRES_IN", data.get("expires_in"))
else:
    print(data)