from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

path = ROOT / "backend" / "app" / "core" / "integration_live_adapter_registry.py"
backup = BACKUPS / f"integration_live_adapter_registry_before_step_s_shopify_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
backup.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

s = path.read_text(encoding="utf-8", errors="ignore")

s = s.replace(
    '''    if integration_key == "store" and action in {"read_products", "create_product_draft", "update_product_draft"}:
        return _execute_shopify_action(tenant_id, connection, action, payload)''',
    '''    if integration_key == "store" and action in {"read_products", "create_product_draft", "update_product_draft", "diagnose_connection"}:
        return _execute_shopify_action(tenant_id, connection, action, payload)''',
)

s = s.replace(
    '''    if action == "read_products":
        return _shopify_read_products(base_url, api_token)''',
    '''    if action == "diagnose_connection":
        return _shopify_diagnose_connection(base_url, api_token)

    if action == "read_products":
        return _shopify_read_products(base_url, api_token)''',
)

if "def _shopify_diagnose_connection" not in s:
    insert_after = '''def _shopify_read_products(base_url: str, api_token: str) -> Dict[str, Any]:
    url = f"{base_url}/admin/api/2025-01/products.json?limit=5"
    result = _shopify_request(url, api_token, method="GET")
    result.update({
        "mode": "live_shopify_read_products",
        "provider": "Shopify",
        "action": "read_products",
    })
    return result
'''
    diagnostic = r'''


def _shopify_diagnose_connection(base_url: str, api_token: str) -> Dict[str, Any]:
    token = str(api_token or "")
    token_type = (
        "admin_api_private_app_token"
        if token.startswith("shpat_")
        else "shopify_app_automation_token"
        if token.startswith("atkn_")
        else "shopify_secret"
        if token.startswith("shpss_")
        else "unknown_token_format"
    )

    shop_response = _shopify_request(
        f"{base_url}/admin/api/2025-01/shop.json",
        api_token,
        method="GET",
    )

    products_response = _shopify_request(
        f"{base_url}/admin/api/2025-01/products.json?limit=1",
        api_token,
        method="GET",
    )

    return {
        "success": bool(shop_response.get("success") or products_response.get("success")),
        "mode": "shopify_connection_diagnostic",
        "provider": "Shopify",
        "token_type": token_type,
        "token_prefix": token[:5] if token else "",
        "shop_endpoint": {
            "success": shop_response.get("success"),
            "status_code": shop_response.get("status_code"),
            "error": shop_response.get("error"),
            "provider_response": str(shop_response.get("provider_response", ""))[:800],
        },
        "products_endpoint": {
            "success": products_response.get("success"),
            "status_code": products_response.get("status_code"),
            "error": products_response.get("error"),
            "provider_response": str(products_response.get("provider_response", ""))[:800],
        },
        "credential_exposed": False,
        "diagnosis": (
            "Token can access Shopify Admin API."
            if shop_response.get("success") or products_response.get("success")
            else "Token cannot access Shopify Admin API with X-Shopify-Access-Token."
        ),
    }
'''
    if insert_after not in s:
        raise SystemExit("SHOPIFY_READ_PRODUCTS_BLOCK_NOT_FOUND")
    s = s.replace(insert_after, insert_after + diagnostic, 1)

path.write_text(s, encoding="utf-8")

test = ROOT / "test_step_s_shopify_diagnostic.py"
test.write_text(r'''import requests

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"
HEADERS = {
    "x-tenant-id": "client_demo_001",
    "x-actor-role": "customer",
    "Content-Type": "application/json",
}

payload = {
    "integration_key": "store",
    "action": "diagnose_connection",
    "payload": {
        "store_domain": "ncn1m2-ch.myshopify.com"
    },
}

r = requests.post(BASE + "/client/integrations/action", json=payload, headers=HEADERS, timeout=60)
print("shopify_diagnostic", r.status_code, r.text[:3000])
''', encoding="utf-8")

print("STEP_S_SHOPIFY_DIAGNOSTIC_INSTALLED")
print(f"Backup: {backup}")