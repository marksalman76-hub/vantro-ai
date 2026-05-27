def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/ai-media-memory/readiness",
        "/admin/ai-media-memory/brand",
        "/admin/ai-media-memory/character",
        "/admin/ai-media-memory/campaign-style",
        "/admin/ai-media-memory/context",
        "/admin/ai-media-memory/enrich",
        "/admin/ai-media-memory/list",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("AI_MEDIA_BRAND_CHARACTER_MEMORY_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
