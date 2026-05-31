def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/ai-media-router/readiness",
        "/admin/ai-media-router/route",
        "/admin/ai-media-router/routes",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("AI_MEDIA_EXECUTION_ROUTER_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
