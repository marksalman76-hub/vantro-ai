from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

adapter_path = ROOT / "backend" / "app" / "core" / "integration_live_adapter_registry.py"
backup = BACKUPS / f"integration_live_adapter_registry_before_step_m_shopify_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
backup.write_text(adapter_path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

text = adapter_path.read_text(encoding="utf-8", errors="ignore")

if "import urllib.parse" not in text:
    text = text.replace("import urllib.request", "import urllib.request\nimport urllib.parse")

if "def _shopify_store_base_url" not in text:
    text += r'''


def _shopify_store_base_url(store_domain: str) -> str:
    store_domain = str(store_domain or "").strip()
    store_domain = store_domain.replace("https://", "").replace("http://", "").strip("/")
    if not store_domain:
        raise ValueError("store_domain_required")
    return f"https://{store_domain}"


def _execute_shopify_action(tenant_id: str, connection: Dict[str, Any], action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    provider = str(connection.get("provider") or "")
    if provider.lower() != "shopify":
        return {
            "success": False,
            "error": "provider_not_supported_for_store_live_execution",
            "provider": provider,
            "supported_provider": "Shopify",
        }

    api_token = connection.get("credential_value")
    if not api_token:
        return {
            "success": False,
            "error": "credential_not_available",
            "credential_exposed": False,
        }

    store_domain = str(payload.get("store_domain") or payload.get("shop_domain") or "").strip()
    try:
        base_url = _shopify_store_base_url(store_domain)
    except ValueError:
        return {
            "success": False,
            "error": "store_domain_required",
            "message": "Provide Shopify store domain, for example your-store.myshopify.com.",
        }

    if action == "read_products":
        return _shopify_read_products(base_url, api_token)

    if action == "create_product_draft":
        return _shopify_create_product_draft(base_url, api_token, payload)

    if action == "update_product_draft":
        return {
            "success": True,
            "mode": "shopify_update_product_draft_scaffold",
            "provider": "Shopify",
            "action": action,
            "live_execution_ready": False,
            "credential_exposed": False,
            "message": "Update product draft adapter scaffold registered. Product ID targeting is next.",
        }

    return {"success": False, "error": "unsupported_shopify_action", "action": action}


def _shopify_request(url: str, api_token: str, method: str = "GET", payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    data = None
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": api_token,
    }

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return {
                "success": True,
                "status_code": response.status,
                "provider_response": body,
                "credential_exposed": False,
            }
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8")
        return {
            "success": False,
            "error": "shopify_api_error",
            "status_code": error.code,
            "provider_response": body,
            "credential_exposed": False,
        }
    except Exception as error:
        return {
            "success": False,
            "error": "shopify_exception",
            "message": str(error),
            "credential_exposed": False,
        }


def _shopify_read_products(base_url: str, api_token: str) -> Dict[str, Any]:
    url = f"{base_url}/admin/api/2025-01/products.json?limit=5"
    result = _shopify_request(url, api_token, method="GET")
    result.update({
        "mode": "live_shopify_read_products",
        "provider": "Shopify",
        "action": "read_products",
    })
    return result


def _shopify_create_product_draft(base_url: str, api_token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    title = str(payload.get("title") or "AI Generated Product Draft").strip()
    body_html = str(payload.get("body_html") or payload.get("description") or "<p>Product draft created by Ecommerce AI Agent Platform.</p>").strip()
    vendor = str(payload.get("vendor") or "AI Generated").strip()
    product_type = str(payload.get("product_type") or "General").strip()
    price = str(payload.get("price") or "0.00").strip()
    sku = str(payload.get("sku") or "AI-DRAFT").strip()

    shopify_payload = {
        "product": {
            "title": title,
            "body_html": body_html,
            "vendor": vendor,
            "product_type": product_type,
            "status": "draft",
            "variants": [
                {
                    "price": price,
                    "sku": sku,
                }
            ],
        }
    }

    url = f"{base_url}/admin/api/2025-01/products.json"
    result = _shopify_request(url, api_token, method="POST", payload=shopify_payload)
    result.update({
        "mode": "live_shopify_create_product_draft",
        "provider": "Shopify",
        "action": "create_product_draft",
        "title": title,
        "status": "draft",
    })
    return result
'''

text = text.replace(
    'if integration_key == "email" and action == "send_email":\n        return _send_email_via_brevo(tenant_id, connection, payload)',
    '''if integration_key == "email" and action == "send_email":
        return _send_email_via_brevo(tenant_id, connection, payload)

    if integration_key == "store" and action in {"read_products", "create_product_draft", "update_product_draft"}:
        return _execute_shopify_action(tenant_id, connection, action, payload)''',
)

adapter_path.write_text(text, encoding="utf-8")

test_path = ROOT / "test_step_m_shopify_global_adapter.py"
test_path.write_text(r'''import requests

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"
HEADERS = {
    "x-tenant-id": "client_demo_001",
    "x-actor-role": "customer",
    "Content-Type": "application/json",
}

registry = requests.get(BASE + "/admin/integrations/live-adapter-registry", timeout=60)
print("registry", registry.status_code, registry.text[:1000])

payload = {
    "integration_key": "store",
    "action": "read_products",
    "payload": {
        "store_domain": "REPLACE_WITH_SHOPIFY_STORE_DOMAIN"
    },
}

r = requests.post(BASE + "/client/integrations/action", json=payload, headers=HEADERS, timeout=60)
print("shopify_read_products", r.status_code, r.text[:2000])
''', encoding="utf-8")

print("STEP_M_SHOPIFY_GLOBAL_ADAPTER_INSTALLED")
print(f"Backup: {backup}")