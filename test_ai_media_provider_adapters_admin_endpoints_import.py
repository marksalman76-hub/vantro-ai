def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/ai-media-adapters/readiness",
        "/admin/ai-media-adapters/status",
        "/admin/ai-media-adapters/prepare",
        "/admin/ai-media-adapters/execute",
        "/admin/ai-media-adapters/results",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("AI_MEDIA_PROVIDER_ADAPTERS_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
