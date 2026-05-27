from backend.app.main import app


def main():
    routes = sorted([getattr(route, "path", "") for route in app.routes])

    required = [
        "/admin/orchestration/readiness",
        "/admin/orchestration/create-test",
        "/admin/orchestration/task-complete",
        "/admin/orchestration/task-fail",
        "/admin/orchestration/{orchestration_id}",
    ]

    print("CROSS_AGENT_ORCHESTRATION_ADMIN_ENDPOINT_IMPORT_TEST")
    for route in required:
        print(route, route in routes)
        assert route in routes

    print("CROSS_AGENT_ORCHESTRATION_ADMIN_ENDPOINT_IMPORT_OK")


if __name__ == "__main__":
    main()
