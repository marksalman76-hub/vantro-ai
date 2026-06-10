from backend.app.runtime.async_media_job_foundation import _apply_final_deliverable_fallback_package


def test_final_deliverable_fallback_package():
    job = {
        "job_id": "media_job_test",
        "status": "partial_success",
        "final_combined_asset_required": True,
        "final_combined_asset_ready": False,
        "final_combined_asset_status": "pending_composition",
        "final_assets": [
            {
                "asset_id": "asset_audio_1",
                "asset_type": "audio",
                "playable": True,
                "preview_ready": True,
                "download_ready": True,
                "signed_delivery_created": True,
                "credential_values_exposed": False,
            }
        ],
        "credential_values_exposed": False,
    }

    result = _apply_final_deliverable_fallback_package(job)

    assert result["final_deliverable_ready"] is True, result
    assert result["final_deliverable_type"] == "fallback_asset_package", result
    assert result["final_deliverable_status"] == "ready", result
    assert result["final_deliverable_asset_ids"] == ["asset_audio_1"], result
    assert result["final_deliverable_primary_asset_id"] == "asset_audio_1", result
    assert result["final_deliverable_asset_count"] == 1, result
    assert result["final_combined_asset_ready"] is False, result
    assert result["final_combined_asset_status"] == "fallback_package_ready", result
    assert result["client_ready_delivery"] is True, result
    assert result["credential_values_exposed"] is False, result


if __name__ == "__main__":
    test_final_deliverable_fallback_package()
    print("FINAL_DELIVERABLE_FALLBACK_PACKAGE_TEST_PASSED")
