import pytest

from app.runtime.creative_provider_routing import (
    CREATIVE_AGENT_IDS,
    creative_provider_status,
    is_creative_agent,
    normalize_creative_agent_id,
    resolve_creative_provider_route,
)


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
