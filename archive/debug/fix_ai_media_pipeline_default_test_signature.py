from pathlib import Path

test_file = Path("test_ai_media_pipeline_creative_director_default.py")

if not test_file.exists():
    raise SystemExit("test_ai_media_pipeline_creative_director_default.py not found")

test_file.write_text(r'''
from backend.app.runtime.ai_media_end_to_end_pipeline import run_ai_media_end_to_end_pipeline


def main():
    result = run_ai_media_end_to_end_pipeline(
        tenant_id="tenant_test",
        brand_name="Default Fix Brand",
        media_type="ugc video",
        objective="premium UGC ad",
        product_or_offer="Default Fix Product",
        target_platform="TikTok",
        region="global",
        audience="online shoppers",
        benefit="clear product value",
        cta="Shop now",
        entitlement_active=True,
        live_keys_available=False,
        preferred_provider="stub_provider",
        context={},
    )

    assert isinstance(result, dict)
    assert result.get("run_id")
    assert result.get("status") in {"prepared", "ready_for_provider_execution", "blocked_by_quality_gate", "pending_owner_approval"}
    assert result.get("execution_allowed") is True

    print("AI_MEDIA_PIPELINE_CREATIVE_DIRECTOR_DEFAULT_OK")


if __name__ == "__main__":
    main()
'''.strip() + "\n", encoding="utf-8")

print("AI_MEDIA_PIPELINE_DEFAULT_TEST_SIGNATURE_FIXED")
print(f"Updated: {test_file}")