def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/ai-media-pipeline/readiness",
        "/admin/ai-media-pipeline/run",
        "/admin/ai-media-pipeline/runs",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("AI_MEDIA_END_TO_END_PIPELINE_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
