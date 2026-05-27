from backend.app.main import app

routes = sorted([getattr(route, "path", "") for route in app.routes])

required = [
    "/admin/provider-adapters/status/{provider_key}",
    "/admin/provider-adapters/normalise",
    "/admin/provider-adapters/route",
    "/admin/provider-adapters/execute-scaffold",
]

missing = [route for route in required if route not in routes]
assert not missing, f"Missing routes: {missing}"

print("REAL_PROVIDER_ADAPTER_ADMIN_ROUTES_TEST_PASSED")
for route in required:
    print(route)
