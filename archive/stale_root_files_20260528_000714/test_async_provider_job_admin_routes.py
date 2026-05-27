from backend.app.main import app

routes = sorted([getattr(route, "path", "") for route in app.routes])

required = [
    "/admin/provider-jobs/create",
    "/admin/provider-jobs/list",
    "/admin/provider-jobs/{job_id}",
    "/admin/provider-jobs/{job_id}/status",
    "/admin/provider-jobs/{job_id}/retry",
]

missing = [route for route in required if route not in routes]
assert not missing, f"Missing routes: {missing}"

print("ASYNC_PROVIDER_JOB_ADMIN_ROUTES_TEST_PASSED")
for route in required:
    print(route)
