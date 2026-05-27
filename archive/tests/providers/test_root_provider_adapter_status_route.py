from backend.app.main import app

routes = sorted([getattr(route, "path", "") for route in app.routes])

required = "/provider-adapter-unified-status/{provider_key}"
assert required in routes, f"Missing route: {required}"

print("ROOT_PROVIDER_ADAPTER_STATUS_ROUTE_TEST_PASSED")
print(required)
