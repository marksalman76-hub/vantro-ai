from pathlib import Path
from backend.app.runtime.durable_media_asset_store import get_media_asset_store


def main():
    store = get_media_asset_store()

    saved = store.save_bytes(
        data=b"fake media bytes for durable asset test",
        filename="final-test.mp4",
        asset_type="final_video",
        job_id="durable_media_job_test_001",
        tenant_id="tenant_test",
        client_id="client_test",
        metadata={
            "duration_seconds": 30,
            "human_mode": "Use client-uploaded face/likeness",
            "content_quality": "test only",
        },
        content_type="video/mp4",
    )

    assert saved["success"] is True
    assert saved["asset_id"]
    assert saved["storage_backend"] == "local_dev"
    assert saved["asset_type"] == "final_video"
    assert saved["content_type"] == "video/mp4"
    assert saved["size_bytes"] > 0
    assert saved["credential_values_exposed"] is False

    loaded = store.get_asset(saved["asset_id"])
    assert loaded["success"] is True
    assert loaded["asset_id"] == saved["asset_id"]
    assert loaded["metadata"]["human_mode"] == "Use client-uploaded face/likeness"

    bytes_result = store.get_asset_bytes(saved["asset_id"])
    assert bytes_result["success"] is True
    assert bytes_result["bytes"] == b"fake media bytes for durable asset test"
    assert bytes_result["checksum_sha256"] == saved["checksum_sha256"]

    signed = store.create_signed_url(saved["asset_id"])
    assert signed["success"] is True
    assert signed["signed_url"].startswith("local://")

    listed = store.list_assets(job_id="durable_media_job_test_001")
    assert listed["success"] is True
    assert listed["count"] >= 1

    temp_file = Path("runtime_outputs") / "durable_asset_test_source.txt"
    temp_file.parent.mkdir(parents=True, exist_ok=True)
    temp_file.write_text("uploaded likeness placeholder", encoding="utf-8")

    uploaded = store.save_file(
        source_path=str(temp_file),
        asset_type="uploaded_likeness_reference",
        job_id="durable_media_job_test_002",
        metadata={
            "explicit_likeness_consent": True,
            "privacy_safe_storage": True,
        },
        content_type="text/plain",
    )
    assert uploaded["success"] is True
    assert uploaded["asset_type"] == "uploaded_likeness_reference"
    assert uploaded["metadata"]["explicit_likeness_consent"] is True

    print("DURABLE_MEDIA_ASSET_STORE_TEST_PASSED")
    print("asset_id:", saved["asset_id"])
    print("uploaded_likeness_asset_id:", uploaded["asset_id"])


if __name__ == "__main__":
    main()
