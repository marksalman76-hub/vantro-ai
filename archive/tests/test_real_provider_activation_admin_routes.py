from backend.app.main import app

routes = sorted([getattr(route, "path", "") for route in app.routes])

required = [
    "/admin/provider-activation/status",
    "/admin/provider-activation/status/{provider_key}",
    "/admin/provider-activation/select/{capability}",
]

missing = [route for route in required if route not in routes]
assert not missing, f"Missing routes: {missing}"

print("REAL_PROVIDER_ACTIVATION_ADMIN_ROUTES_TEST_PASSED")
for route in required:
    print(route)
