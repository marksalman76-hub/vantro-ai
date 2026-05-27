def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/ai-media/readiness",
        "/admin/ai-media/models",
        "/admin/ai-media/creative-plan",
        "/admin/ai-media/creative-plans",
        "/admin/ai-media/execution-packet",
        "/admin/ai-media/execution-packets",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("AI_MEDIA_CREATIVE_MODEL_REGISTRY_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
