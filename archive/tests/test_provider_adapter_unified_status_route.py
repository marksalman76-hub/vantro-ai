from backend.app.main import app

routes = sorted([getattr(route, "path", "") for route in app.routes])

required = "/admin/provider-adapters/unified-status/{provider_key}"

assert required in routes, f"Missing route: {required}"

print("PROVIDER_ADAPTER_UNIFIED_STATUS_ROUTE_TEST_PASSED")
print(required)
