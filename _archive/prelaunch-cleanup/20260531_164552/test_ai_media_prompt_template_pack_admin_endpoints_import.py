def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/ai-media-templates/readiness",
        "/admin/ai-media-templates/list",
        "/admin/ai-media-templates/recommend",
        "/admin/ai-media-templates/render",
        "/admin/ai-media-templates/rendered",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("AI_MEDIA_PROMPT_TEMPLATE_PACK_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
