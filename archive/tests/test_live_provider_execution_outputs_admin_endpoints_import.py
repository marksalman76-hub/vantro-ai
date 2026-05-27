def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/live-provider-execution/readiness",
        "/admin/live-provider-execution/execute",
        "/admin/live-provider-execution/list",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("LIVE_PROVIDER_EXECUTION_OUTPUTS_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
