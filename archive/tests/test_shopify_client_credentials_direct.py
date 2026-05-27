import getpass
import requests

SHOP = "ncn1m2-ch.myshopify.com"

CLIENT_ID = "83d3f6f05643e5297f59bca36ee4244d"
CLIENT_SECRET = getpass.getpass("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: ").strip()

url = f"https://{SHOP}/admin/oauth/access_token"

response = requests.post(
    url,
    data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    },
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    timeout=60,
)

print("HTTP", response.status_code)
print(response.text[:4000])