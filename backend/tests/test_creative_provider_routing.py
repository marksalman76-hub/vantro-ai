import pytest

from app.agents import agent_worker
from app.integrations.execution_adapters import AdapterResult
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


@pytest.mark.parametrize("agent_id", CREATIVE_AGENT_CASES)
def test_every_creative_agent_resolves_video_models(agent_id):
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


@pytest.mark.parametrize("agent_id", CREATIVE_AGENT_CASES)
def test_every_creative_agent_resolves_image_models(agent_id):
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
        agent_id="ugc_media_agent",
        media_type="video",
        video_quality=quality,
    )

    assert route["video"]["provider"] == "higgsfield"
    assert route["video"]["model"] == expected_model


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


@pytest.mark.parametrize("agent_id", CREATIVE_AGENT_CASES)
def test_provider_stack_gives_creative_agents_higgsfield_and_nano_banana(agent_id):
    providers = providers_for_agent(agent_id)

    assert "higgsfield" in providers
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
        agent_id="ugc_media_agent",
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
    assert result.execution_payload["selected_image_provider"] == "nano_banana"
    assert result.execution_payload["selected_image_model"] == "Nano Banana Pro"
    assert result.provider_ready is False


def test_execution_adapter_keeps_image_route_metadata_but_disables_live_video_for_image_only_routes(monkeypatch):
    monkeypatch.setenv("HIGGSFIELD_API_KEY", "test-key")

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
