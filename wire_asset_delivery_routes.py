from pathlib import Path
from datetime import datetime

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
main_path = root / "backend" / "app" / "main.py"

text = main_path.read_text(encoding="utf-8")

backup_dir = root / "backups" / f"main_before_asset_delivery_routes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
(backup_dir / "main.py").write_text(text, encoding="utf-8")

if "build_customer_safe_delivery_response" not in text:
    import_marker = "from backend.app.runtime.creative_asset_persistence_bridge import get_persisted_creative_assets, persist_creative_agent_output"
    replacement = import_marker + "\nfrom backend.app.runtime.asset_storage_signed_delivery_runtime import build_customer_safe_delivery_response"
    if import_marker not in text:
        raise SystemExit("Import marker not found. No changes made.")
    text = text.replace(import_marker, replacement)

route_marker = "# PRODUCTION_ASSET_DELIVERY_ROUTES_START"

route_block = '''
# PRODUCTION_ASSET_DELIVERY_ROUTES_START
@app.get("/asset-delivery/{delivery_type}/{asset_id}")
async def asset_delivery_route(delivery_type: str, asset_id: str, expires: int, nonce: str, sig: str):
    try:
        result = build_customer_safe_delivery_response(
            asset_id=asset_id,
            delivery_type=delivery_type,
            expires_at_ms=expires,
            nonce=nonce,
            signature=sig,
        )
        status_code = int(result.get("http_status", 200))
        if status_code >= 400:
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=status_code, content=result)
        return result
    except Exception as exc:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status": "error",
                "reason": "asset_delivery_route_failed",
                "error": str(exc),
                "credential_values_exposed": False,
                "customer_safe": True,
            },
        )
# PRODUCTION_ASSET_DELIVERY_ROUTES_END
'''

if route_marker not in text:
    insert_marker = '@app.get("/admin/persisted-creative-assets")'
    index = text.index(insert_marker)
    text = text[:index] + route_block + "\n" + text[index:]

main_path.write_text(text, encoding="utf-8")

print("ASSET_DELIVERY_ROUTES_WIRED")
print("Backup:", backup_dir)