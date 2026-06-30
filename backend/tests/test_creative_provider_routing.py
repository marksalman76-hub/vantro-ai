import pytest

from app.agents import agent_worker
from app.integrations.execution_adapters import AdapterResult, adapter_summary
from app.agents.agent_worker import _build_media_generation_output
from app.runtime.creative_provider_routing import (
    CREATIVE_AGENT_IDS,
    creative_provider_status,
    is_creative_agent,
    normalize_creative_agent_id,
    resolve_creative_provider_route,
)
from app.runtime.audio_visual_provider_stack import (
    full_provider_stack_status,
    provider_config_status,
    providers_for_agent,
    recommended_stack_for_task,
)
from app.integrations.execution_adapters import ExecutionAdapters


CREATIVE_AGENT_CASES = [
    "ugc_media_agent",
    "ugc_creative_agent",
    "product_image_agent",
    "ad_creative_agent",
    "creative_rotation_agent",
    "social_media_content_agent",
    "ads_optimisation_agent",
]

VIDEO_CAPABLE_AGENT_CASES = [
    "ugc_media_agent",
    "ugc_creative_agent",
    "ad_creative_agent",
    "creative_rotation_agent",
    "social_media_content_agent",
]

PRO_IMAGE_CAPABLE_AGENT_CASES = [
    "ugc_creative_agent",
    "product_image_agent",
    "ad_creative_agent",
]


@pytest.mark.parametrize("agent_id", VIDEO_CAPABLE_AGENT_CASES)
def test_video_capable_creative_agents_resolve_lower_tier_video_model(agent_id):
    route = resolve_creative_provider_route(
        agent_id=agent_id,
        media_type="video",
        video_quality="720p",
    )

    assert route["success"] is True
    assert route["agent_id"] == agent_id
    assert route["canonical_agent_id"] in CREATIVE_AGENT_IDS
    assert route["video"]["provider"] == "higgsfield"
    assert route["video"]["model"] == "Kling 3.0 Turbo"
    assert route["video"]["quality"] == "720p"
    assert route["credential_values_exposed"] is False


@pytest.mark.parametrize("agent_id", PRO_IMAGE_CAPABLE_AGENT_CASES)
def test_pro_image_capable_creative_agents_resolve_premium_image_model(agent_id):
    route = resolve_creative_provider_route(
        agent_id=agent_id,
        media_type="image",
        image_tier="premium",
    )

    assert route["success"] is True
    assert route["image"]["provider"] == "nano_banana"
    assert route["image"]["model"] == "Nano Banana Pro"
    assert route["image"]["tier"] == "premium"
    assert route["credential_values_exposed"] is False


@pytest.mark.parametrize(
    ("quality", "expected_model"),
    [
        ("720p", "Kling 3.0 Turbo"),
        ("1080p", "Kling 3.0"),
        ("4K", "Cinema Studio 4K"),
        ("", "Kling 3.0"),
        ("unknown", "Kling 3.0"),
    ],
)
def test_video_quality_selects_higgsfield_model(quality, expected_model):
    route = resolve_creative_provider_route(
        agent_id="ugc_creative_agent",
        media_type="video",
        video_quality=quality,
    )

    assert route["video"]["provider"] == "higgsfield"
    assert route["video"]["model"] == expected_model
    assert route["video"]["model_id"]


@pytest.mark.parametrize(
    ("tier", "expected_model"),
    [
        ("standard", "Nano Banana 2"),
        ("production", "Nano Banana 2"),
        ("", "Nano Banana 2"),
        ("premium", "Nano Banana Pro"),
        ("pro", "Nano Banana Pro"),
    ],
)
def test_image_tier_selects_nano_banana_model(tier, expected_model):
    route = resolve_creative_provider_route(
        agent_id="product_image_agent",
        media_type="image",
        image_tier=tier,
    )

    assert route["image"]["provider"] == "nano_banana"
    assert route["image"]["model"] == expected_model


@pytest.mark.parametrize(
    ("alias", "canonical"),
    [
        ("paid_ads_agent", "ads_optimisation_agent"),
        ("social_media_manager_content_creator_agent", "social_media_content_agent"),
        ("product_video_agent", "ugc_media_agent"),
    ],
)
def test_alias_ids_resolve_to_canonical_creative_agents(alias, canonical):
    assert normalize_creative_agent_id(alias) == canonical
    assert is_creative_agent(alias) is True


def test_unknown_agent_returns_clear_failure():
    route = resolve_creative_provider_route(
        agent_id="finance_admin_agent",
        media_type="video",
    )

    assert route["success"] is False
    assert route["reason"] == "unknown_creative_agent"
    assert route["credential_values_exposed"] is False


@pytest.mark.parametrize(
    "request_context",
    [
        {"media_type": "video"},
        {"media_request": {"media_type": "video"}},
    ],
)
def test_request_context_media_type_overrides_default_media_type(request_context):
    route = resolve_creative_provider_route(
        agent_id="ugc_media_agent",
        request_context=request_context,
    )

    assert route["success"] is True
    assert route["media_types"] == ["video"]
    assert "video" in route
    assert "image" not in route


def test_creative_provider_status_exposes_models_without_credentials():
    status = creative_provider_status()

    assert status["success"] is True
    assert status["providers"]["higgsfield"]["models"] == [
        "Kling 3.0 Turbo",
        "Kling 3.0",
        "Cinema Studio 4K",
    ]
    assert status["providers"]["higgsfield"]["model_ids"] == [
        "kling3_0_turbo",
        "kling3_0",
        "cinematic_studio_3_0",
    ]
    assert status["providers"]["nano_banana"]["models"] == [
        "Nano Banana 2",
        "Nano Banana Pro",
    ]
    assert status["credential_values_exposed"] is False


def test_provider_stack_exposes_higgsfield_and_nano_banana():
    status = full_provider_stack_status()

    assert "higgsfield" in status["providers"]
    assert "nano_banana" in status["providers"]
    assert status["providers"]["higgsfield"]["models"] == [
        "Kling 3.0 Turbo",
        "Kling 3.0",
        "Cinema Studio 4K",
    ]
    assert status["providers"]["nano_banana"]["models"] == [
        "Nano Banana 2",
        "Nano Banana Pro",
    ]
    assert status["credential_values_exposed"] is False


@pytest.mark.parametrize("agent_id", VIDEO_CAPABLE_AGENT_CASES)
def test_provider_stack_gives_video_capable_agents_higgsfield(agent_id):
    providers = providers_for_agent(agent_id)

    assert "higgsfield" in providers


@pytest.mark.parametrize("agent_id", CREATIVE_AGENT_CASES)
def test_provider_stack_gives_image_capable_agents_nano_banana(agent_id):
    providers = providers_for_agent(agent_id)

    if agent_id != "ugc_media_agent":
        assert "nano_banana" in providers


@pytest.mark.parametrize(
    "alias",
    [
        "paid_ads_agent",
        "social_media_manager_content_creator_agent",
    ],
)
def test_provider_stack_normalizes_creative_aliases(alias):
    providers = providers_for_agent(alias)

    assert "nano_banana" in providers


def test_recommended_stack_prioritizes_higgsfield_for_video_and_nano_banana_for_image():
    video_stack = recommended_stack_for_task("ugc_media_agent", "Create a 720p product video")
    image_stack = recommended_stack_for_task("product_image_agent", "Create a premium product image")

    assert video_stack["recommended_order"][0] == "higgsfield"
    assert image_stack["recommended_order"][0] == "nano_banana"


def test_provider_config_status_keeps_credentials_hidden():
    status = provider_config_status("higgsfield")

    assert status["provider"] == "higgsfield"
    assert "credential_values_exposed" in status
    assert status["credential_values_exposed"] is False
    assert "api_key" not in str(status).lower()


def test_execution_adapter_preserves_selected_creative_models_without_credentials():
    adapter = ExecutionAdapters(db=None)
    route = resolve_creative_provider_route(
        agent_id="ugc_creative_agent",
        media_type="both",
        video_quality="4K",
        image_tier="pro",
    )

    result = adapter.execute(
        adapter_name="ugc_video_provider_adapter",
        payload={
            "workflow": {
                "tenant_id": "workspace-test",
                "task": "Create a cinematic product launch clip",
                "creative_provider_route": route,
            },
            "context": {
                "agent_id": "ugc_media_agent",
                "job_id": "job-test",
                "creative_provider_route": route,
            },
        },
    )

    assert result.execution_payload["selected_video_provider"] == "higgsfield"
    assert result.execution_payload["selected_video_model"] == "Cinema Studio 4K"
    assert result.execution_payload["selected_video_model_id"] == "cinematic_studio_3_0"
    assert result.execution_payload["selected_image_provider"] == "nano_banana"
    assert result.execution_payload["selected_image_model"] == "Nano Banana Pro"
    assert result.provider_ready is False


def test_execution_adapter_preserves_media_request_and_voiceover_metadata():
    adapter = ExecutionAdapters(db=None)
    route = resolve_creative_provider_route(
        agent_id="ugc_creative_agent",
        media_type="video",
        video_quality="4K",
    )
    media_request = {
        "platform": "Instagram Reels",
        "aspect_ratio": "16:9 (landscape)",
        "tone": "Luxury",
        "language": "Spanish",
        "video_quality": "4K",
    }

    result = adapter.execute(
        adapter_name="ugc_video_provider_adapter",
        payload={
            "workflow": {
                "tenant_id": "workspace-test",
                "task": "Create a Spanish product launch clip",
                "language": "Spanish",
                "media_request": media_request,
                "voiceover": {
                    "provider": "elevenlabs",
                    "model_id": "eleven_multilingual_v2",
                    "language": "Spanish",
                    "multilingual": True,
                },
                "creative_provider_route": route,
            },
            "context": {
                "agent_id": "ugc_creative_agent",
                "job_id": "job-test",
                "media_request": media_request,
                "creative_provider_route": route,
            },
        },
    )

    assert result.execution_payload["language"] == "Spanish"
    assert result.execution_payload["media_request"] == media_request
    assert result.execution_payload["voiceover"]["provider"] == "elevenlabs"
    assert result.execution_payload["voiceover"]["model_id"] == "eleven_multilingual_v2"


def test_execution_adapter_requires_live_flag_with_higgsfield_credentials(monkeypatch):
    monkeypatch.setenv("HIGGSFIELD_API_KEY", "test-key")
    monkeypatch.setenv("HIGGSFIELD_EXECUTION_SURFACE", "api_key")
    monkeypatch.delenv("HIGGSFIELD_LIVE_EXECUTION_ENABLED", raising=False)

    adapter = ExecutionAdapters(db=None)
    route = resolve_creative_provider_route(
        agent_id="ugc_creative_agent",
        media_type="video",
        video_quality="4K",
    )

    result = adapter.execute(
        adapter_name="ugc_video_provider_adapter",
        payload={
            "workflow": {
                "tenant_id": "workspace-test",
                "task": "Create a cinematic product launch clip",
                "creative_provider_route": route,
            },
            "context": {
                "agent_id": "ugc_media_agent",
                "job_id": "job-test",
                "creative_provider_route": route,
            },
        },
    )

    assert result.provider_ready is False
    assert result.execution_mode == "provider_orchestrated_safe_stub"
    assert result.execution_payload["provider_connected"] is True


def test_execution_adapter_requires_credentials_and_live_flag_for_higgsfield_live(monkeypatch):
    monkeypatch.setenv("HIGGSFIELD_API_KEY", "test-key")
    monkeypatch.setenv("HIGGSFIELD_EXECUTION_SURFACE", "api_key")
    monkeypatch.setenv("HIGGSFIELD_LIVE_EXECUTION_ENABLED", "true")

    adapter = ExecutionAdapters(db=None)
    route = resolve_creative_provider_route(
        agent_id="ugc_creative_agent",
        media_type="video",
        video_quality="4K",
    )

    result = adapter.execute(
        adapter_name="ugc_video_provider_adapter",
        payload={
            "workflow": {
                "tenant_id": "workspace-test",
                "task": "Create a cinematic product launch clip",
                "creative_provider_route": route,
            },
            "context": {
                "agent_id": "ugc_media_agent",
                "job_id": "job-test",
                "creative_provider_route": route,
            },
        },
    )

    assert result.provider_ready is True
    assert result.execution_mode == "higgsfield_live"
    assert result.execution_payload["provider_instance"].is_ready() is True


def test_execution_adapter_uses_higgsfield_claude_mcp_without_api_key(monkeypatch):
    monkeypatch.delenv("HIGGSFIELD_API_KEY", raising=False)
    monkeypatch.setenv("HIGGSFIELD_LIVE_EXECUTION_ENABLED", "true")
    monkeypatch.setenv("HIGGSFIELD_EXECUTION_SURFACE", "claude_code_mcp")
    monkeypatch.setattr(
        "app.integrations.execution_adapters.HiggsfieldProvider.is_mcp_ready",
        lambda self: True,
    )

    adapter = ExecutionAdapters(db=None)
    route = resolve_creative_provider_route(
        agent_id="ugc_media_agent",
        media_type="video",
        video_quality="720p",
    )

    result = adapter.execute(
        adapter_name="ugc_video_provider_adapter",
        payload={
            "workflow": {
                "tenant_id": "workspace-test",
                "task": "Create a product clip",
                "creative_provider_route": route,
            },
            "context": {
                "agent_id": "ugc_media_agent",
                "job_id": "job-test",
                "creative_provider_route": route,
            },
        },
    )

    assert result.provider_ready is True
    assert result.execution_mode == "higgsfield_mcp_live"
    assert result.execution_payload["execution_surface"] == "claude_code_mcp"
    assert result.execution_payload["provider_connected"] is True
    assert result.execution_payload["selected_video_model_id"] == "kling3_0_turbo"


def test_adapter_summary_drops_provider_instance_but_internal_result_keeps_it(monkeypatch):
    monkeypatch.setenv("HIGGSFIELD_API_KEY", "test-key")
    monkeypatch.setenv("HIGGSFIELD_EXECUTION_SURFACE", "api_key")
    monkeypatch.setenv("HIGGSFIELD_LIVE_EXECUTION_ENABLED", "true")

    adapter = ExecutionAdapters(db=None)
    route = resolve_creative_provider_route(
        agent_id="ugc_media_agent",
        media_type="video",
    )

    result = adapter.execute(
        adapter_name="ugc_video_provider_adapter",
        payload={
            "workflow": {
                "tenant_id": "workspace-test",
                "task": "Create a product video",
                "creative_provider_route": route,
            },
            "context": {
                "agent_id": "ugc_media_agent",
                "job_id": "job-test",
                "creative_provider_route": route,
            },
        },
    )

    assert result.execution_payload["provider_instance"].is_ready() is True
    summary = adapter_summary(result)

    assert "provider_instance" not in summary["execution_payload"]
    assert summary["execution_payload"]["selected_video_provider"] == "higgsfield"


def test_execution_adapter_keeps_image_route_metadata_but_disables_live_video_for_image_only_routes(monkeypatch):
    monkeypatch.setenv("HIGGSFIELD_API_KEY", "test-key")
    monkeypatch.setenv("HIGGSFIELD_EXECUTION_SURFACE", "api_key")

    adapter = ExecutionAdapters(db=None)
    route = resolve_creative_provider_route(
        agent_id="product_image_agent",
        media_type="image",
        image_tier="pro",
    )

    result = adapter.execute(
        adapter_name="ugc_video_provider_adapter",
        payload={
            "workflow": {
                "tenant_id": "workspace-test",
                "task": "Create premium skincare product renders",
                "creative_provider_route": route,
            },
            "context": {
                "agent_id": "product_image_agent",
                "job_id": "job-test",
                "creative_provider_route": route,
            },
        },
    )

    assert result.execution_payload["selected_image_provider"] == "nano_banana"
    assert result.execution_payload["selected_image_model"] == "Nano Banana Pro"
    assert result.execution_payload["selected_video_provider"] is None
    assert result.execution_payload["selected_video_model"] is None
    assert result.provider_ready is False


def test_worker_live_execution_guard_requires_selected_video_route():
    adapter_result = AdapterResult(
        success=True,
        adapter_name="ugc_video_provider_adapter",
        execution_mode="higgsfield_live",
        provider_ready=True,
        message="prepared",
        next_steps=[],
        execution_payload={
            "selected_video_provider": None,
            "selected_video_model": None,
            "selected_image_provider": "nano_banana",
            "selected_image_model": "Nano Banana Pro",
        },
    )

    assert agent_worker._should_execute_higgsfield_live(  # type: ignore[attr-defined]
        adapter_result,
        {
            "success": True,
            "media_types": ["image"],
            "image": {"provider": "nano_banana", "model": "Nano Banana Pro"},
        },
    ) is False


def test_worker_builds_higgsfield_kwargs_from_create_media_request(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
    route = resolve_creative_provider_route(
        agent_id="ugc_creative_agent",
        media_type="video",
        video_quality="4K",
        package_tier="enterprise",
    )
    adapter_result = AdapterResult(
        success=True,
        adapter_name="ugc_video_provider_adapter",
        execution_mode="higgsfield_live",
        provider_ready=True,
        message="prepared",
        next_steps=[],
        execution_payload={
            "selected_video_provider": "higgsfield",
            "selected_video_model": "Cinema Studio 4K",
            "selected_video_model_id": "cinematic_studio_3_0",
        },
    )

    kwargs = agent_worker._build_higgsfield_execution_kwargs(  # type: ignore[attr-defined]
        {
            "media_request": {
                "platform": "Instagram Reels",
                "aspect_ratio": "16:9 (landscape)",
                "tone": "Luxury",
                "language": "Spanish",
                "video_quality": "4K",
                "voiceover_script": "Descubre nuestra nueva coleccion premium.",
            }
        },
        adapter_result,
    )

    assert kwargs["model"] == "cinematic_studio_3_0"
    assert kwargs["platform"] == "instagram reels"
    assert kwargs["aspect_ratio"] == "16:9"
    assert kwargs["tone"] == "luxury"
    assert kwargs["quality"] == "4K"
    assert kwargs["language"] == "Spanish"
    assert kwargs["voice_provider"] == "elevenlabs"
    assert kwargs["voice_model_id"] == "eleven_multilingual_v2"
    assert kwargs["voice_language"] == "Spanish"
    assert kwargs["voiceover_script"] == "Descubre nuestra nueva coleccion premium."
    assert kwargs["multilingual_voice_enabled"] is True


def test_worker_media_preview_packet_preserves_provider_readiness_when_live_asset_missing():
    route = resolve_creative_provider_route(
        agent_id="product_image_agent",
        media_type="image",
        image_tier="pro",
        package_tier="enterprise",
    )
    adapter_result = AdapterResult(
        success=False,
        adapter_name="ugc_video_provider_adapter",
        execution_mode="provider_orchestrated_safe_stub",
        provider_ready=False,
        message="Product image generation adapter prepared through provider orchestrator.",
        next_steps=["Connect image provider credentials."],
        execution_payload={
            "selected_video_provider": None,
            "selected_video_model": None,
            "selected_image_provider": "nano_banana",
            "selected_image_model": "Nano Banana Pro",
            "provider_connected": False,
            "live_execution_enabled": False,
        },
    )

    packet = _build_media_generation_output(
        script="Create a premium product image.",
        creative_provider_route=route,
        adapter_result=adapter_result,
        live_task_result=None,
        requested_agent_id="product_image_agent",
        fallback_preview_asset={
            "asset_id": "asset-preview",
            "preview_url": "data:image/svg+xml;base64,abc",
            "asset_url": "data:image/svg+xml;base64,abc",
            "provider": "local_visual_generation_runtime",
            "fallback_used": True,
        },
    )

    assert packet["type"] == "media_generation"
    assert packet["requested_agent_id"] == "product_image_agent"
    assert packet["real_media_asset_created"] is False
    assert packet["preview_ready"] is True
    assert packet["preview_url"].startswith("data:image/svg+xml")
    assert packet["download_ready"] is True
    assert packet["download_url"].startswith("data:image/svg+xml")
    assert packet["provider_readiness"]["provider_ready"] is False
    assert packet["provider_readiness"]["selected_image_model"] == "Nano Banana Pro"


def test_lower_tier_social_agent_cannot_use_premium_higgsfield_models():
    route = resolve_creative_provider_route(
        agent_id="social_media_content_agent",
        media_type="video",
        video_quality="4K",
        package_tier="enterprise",
    )

    assert route["success"] is False
    assert route["reason"] == "model_not_allowed_for_agent"
    assert route["blocked_model"] == "Cinema Studio 4K"
    assert route["allowed_models"]["video"] == ["Kling 3.0 Turbo"]
    assert route["credential_values_exposed"] is False


def test_starter_package_caps_premium_agent_to_lower_higgsfield_model():
    route = resolve_creative_provider_route(
        agent_id="ugc_creative_agent",
        media_type="video",
        video_quality="1080p",
        package_tier="starter",
    )

    assert route["success"] is False
    assert route["reason"] == "model_not_allowed_for_package"
    assert route["blocked_model"] == "Kling 3.0"
    assert route["allowed_models"]["video"] == ["Kling 3.0 Turbo"]
    assert route["credential_values_exposed"] is False


def test_premium_creative_agent_on_business_can_use_4k_video_and_pro_images():
    route = resolve_creative_provider_route(
        agent_id="ugc_creative_agent",
        media_type="both",
        video_quality="4K",
        image_tier="pro",
        package_tier="business",
    )

    assert route["success"] is True
    assert route["video"]["model"] == "Cinema Studio 4K"
    assert route["image"]["model"] == "Nano Banana Pro"
    assert route["entitlement"]["package_tier"] == "business"


def test_product_image_agent_cannot_request_higgsfield_video():
    route = resolve_creative_provider_route(
        agent_id="product_image_agent",
        media_type="video",
        video_quality="720p",
        package_tier="enterprise",
    )

    assert route["success"] is False
    assert route["reason"] == "media_type_not_allowed_for_agent"
    assert route["blocked_media_type"] == "video"
    assert route["allowed_models"]["image"] == ["Nano Banana 2", "Nano Banana Pro"]


def test_admin_create_media_form_type_social_ad_maps_to_video_route():
    route = resolve_creative_provider_route(
        agent_id="ugc_media_agent",
        request_context={
            "media_request": {
                "type": "social_ad",
                "video_quality": "720p",
            }
        },
        package_tier="enterprise",
    )

    assert route["success"] is True
    assert route["media_types"] == ["video"]
    assert route["video"]["provider"] == "higgsfield"
    assert route["video"]["model"] == "Kling 3.0 Turbo"
