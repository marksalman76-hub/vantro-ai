from backend.app.main import app

routes = sorted([getattr(route, "path", "") for route in app.routes])

required = "/provider-adapter-runtime-status/{provider_key}"
assert required in routes, f"Missing route: {required}"

print("PROVIDER_ADAPTER_RUNTIME_STATUS_ROUTE_TEST_PASSED")
print(required)
