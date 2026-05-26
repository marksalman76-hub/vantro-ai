from backend.app.main import app


def main():
    routes = sorted([getattr(route, "path", "") for route in app.routes])

    required = [
        "/admin/workflows/readiness",
        "/admin/workflows/create-test",
        "/admin/workflows/advance",
        "/admin/workflows/fail",
        "/admin/workflows/complete",
        "/admin/workflows/{workflow_id}",
    ]

    print("PERSISTENT_WORKFLOW_ADMIN_ENDPOINT_IMPORT_TEST")
    for route in required:
        print(route, route in routes)
        assert route in routes

    print("PERSISTENT_WORKFLOW_ADMIN_ENDPOINT_IMPORT_OK")


if __name__ == "__main__":
    main()
