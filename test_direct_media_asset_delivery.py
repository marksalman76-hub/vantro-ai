from backend.app.main import app


def test_direct_media_asset_route_registered():
    paths = {getattr(route, "path", "") for route in app.routes}
    assert "/admin/direct-media-provider-asset/{job_id}" in paths, paths


if __name__ == "__main__":
    test_direct_media_asset_route_registered()
    print("DIRECT_MEDIA_ASSET_DELIVERY_TEST_PASSED")
