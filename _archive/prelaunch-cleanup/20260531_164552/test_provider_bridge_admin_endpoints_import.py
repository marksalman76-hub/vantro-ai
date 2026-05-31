from backend.app.main import app


def main():
    routes = sorted([getattr(route, "path", "") for route in app.routes])

    required = [
        "/admin/provider-connectors/readiness",
        "/admin/provider-bridge/readiness",
        "/admin/provider-bridge/test-safe-generation",
    ]

    print("PROVIDER_BRIDGE_ADMIN_ENDPOINT_IMPORT_TEST")
    for route in required:
        print(route, route in routes)
        assert route in routes

    print("PROVIDER_BRIDGE_ADMIN_ENDPOINT_IMPORT_OK")


if __name__ == "__main__":
    main()
