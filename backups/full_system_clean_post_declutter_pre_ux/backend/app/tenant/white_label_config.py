"""
White-Label Client Configuration

Controls client-safe branding and presentation settings.
Internal configuration, prompts, workflows, and provider details must never
be exposed through this layer.
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class WhiteLabelConfig:
    tenant_id: str
    business_name: str
    logo_url: Optional[str]
    primary_colour: str
    secondary_colour: str
    accent_colour: str
    domain: Optional[str]
    country: str
    region: str
    currency: str
    language: str
    brand_voice: str


CLIENT_SAFE_FIELDS = [
    "tenant_id",
    "business_name",
    "logo_url",
    "primary_colour",
    "secondary_colour",
    "accent_colour",
    "domain",
    "country",
    "region",
    "currency",
    "language",
    "brand_voice",
]


BLOCKED_INTERNAL_FIELDS = [
    "api_key",
    "secret",
    "provider_token",
    "system_prompt",
    "workflow_config",
    "backend_route",
    "internal_reasoning",
    "approval_logic",
    "hidden_scoring",
]


def build_white_label_config(
    tenant_id: str,
    business_name: str,
    logo_url: Optional[str] = None,
    primary_colour: str = "#111827",
    secondary_colour: str = "#ffffff",
    accent_colour: str = "#2563eb",
    domain: Optional[str] = None,
    country: str = "Global",
    region: str = "Global",
    currency: str = "USD",
    language: str = "English",
    brand_voice: str = "premium, clear, trustworthy",
) -> WhiteLabelConfig:
    return WhiteLabelConfig(
        tenant_id=tenant_id,
        business_name=business_name,
        logo_url=logo_url,
        primary_colour=primary_colour,
        secondary_colour=secondary_colour,
        accent_colour=accent_colour,
        domain=domain,
        country=country,
        region=region,
        currency=currency,
        language=language,
        brand_voice=brand_voice,
    )


def client_safe_config(config: WhiteLabelConfig) -> Dict[str, Optional[str]]:
    return {
        field: getattr(config, field)
        for field in CLIENT_SAFE_FIELDS
    }


def contains_blocked_internal_field(payload: Dict[str, object]) -> bool:
    lowered_keys = {str(key).lower() for key in payload.keys()}
    return any(blocked in lowered_keys for blocked in BLOCKED_INTERNAL_FIELDS)