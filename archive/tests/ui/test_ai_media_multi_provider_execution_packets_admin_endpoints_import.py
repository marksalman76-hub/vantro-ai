def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/ai-media-packets/readiness",
        "/admin/ai-media-packets/create",
        "/admin/ai-media-packets/advance-provider",
        "/admin/ai-media-packets/list",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("AI_MEDIA_MULTI_PROVIDER_EXECUTION_PACKETS_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
