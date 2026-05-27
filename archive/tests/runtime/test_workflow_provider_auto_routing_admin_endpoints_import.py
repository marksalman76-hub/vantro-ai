def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/workflow-provider-routing/readiness",
        "/admin/workflow-provider-routing/route",
        "/admin/workflow-provider-routing/list",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("WORKFLOW_PROVIDER_AUTO_ROUTING_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
