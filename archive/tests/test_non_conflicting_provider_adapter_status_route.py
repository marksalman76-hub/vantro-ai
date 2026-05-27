from backend.app.main import app

routes = sorted([getattr(route, "path", "") for route in app.routes])

required = "/admin/unified-provider-adapter-status/{provider_key}"
assert required in routes, f"Missing route: {required}"

print("NON_CONFLICTING_PROVIDER_ADAPTER_STATUS_ROUTE_TEST_PASSED")
print(required)
