def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/dead-letter/readiness",
        "/admin/dead-letter/create",
        "/admin/dead-letter/list",
        "/admin/manual-review/list",
        "/admin/manual-review/decision",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("DEAD_LETTER_MANUAL_REVIEW_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
