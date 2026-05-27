def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/ai-media-quality/readiness",
        "/admin/ai-media-quality/score",
        "/admin/ai-media-quality/gate-packet",
        "/admin/ai-media-quality/scores",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("AI_MEDIA_QUALITY_GATE_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
