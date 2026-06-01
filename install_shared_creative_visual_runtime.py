from pathlib import Path

p = Path("backend/app/runtime/shared_creative_visual_generation_runtime.py")

p.write_text(r'''
from __future__ import annotations

from datetime import datetime
import base64
import html
import os
import uuid
from typing import Dict, Any

from dotenv import load_dotenv

load_dotenv(".env.local")

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


AGENT_VISUAL_PROFILES = {
    "ugc_creative_agent": {
        "label": "UGC Creator Visual",
        "prompt_style": "photorealistic creator-led UGC social media ad, authentic handheld creator aesthetic, premium lighting",
    },
    "product_image_agent": {
        "label": "Product Image Visual",
        "prompt_style": "premium ecommerce product photography, clean luxury studio lighting, high-conversion product hero shot",
    },
    "paid_ads_agent": {
        "label": "Paid Ad Creative Visual",
        "prompt_style": "high-converting social ad creative, premium brand composition, scroll-stopping ad visual",
    },
    "social_media_manager_content_creator_agent": {
        "label": "Social Content Visual",
        "prompt_style": "premium social media content creative, polished lifestyle composition, platform-ready visual",
    },
    "brand_strategy_agent": {
        "label": "Brand Concept Visual",
        "prompt_style": "premium brand moodboard visual, sophisticated art direction, luxury brand identity concept",
    },
    "marketing_specialist_agent": {
        "label": "Marketing Campaign Visual",
        "prompt_style": "premium campaign concept visual, brand-safe commercial creative, polished marketing asset",
    },
}


def _profile_for_agent(agent_id: str) -> Dict[str, str]:
    return AGENT_VISUAL_PROFILES.get(
        agent_id,
        {
            "label": "Creative Visual Asset",
            "prompt_style": "premium commercial creative visual, brand-safe, polished, high-quality",
        },
    )


def _fallback_svg(prompt: str, asset_id: str, agent_id: str):
    profile = _profile_for_agent(agent_id)
    safe_prompt = html.escape(str(prompt or "Premium creative visual concept")[:260])
    safe_label = html.escape(profile["label"])

    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#07111f"/>
      <stop offset="48%" stop-color="#172554"/>
      <stop offset="100%" stop-color="#581c87"/>
    </linearGradient>
    <radialGradient id="glow" cx="74%" cy="28%" r="58%">
      <stop offset="0%" stop-color="#fde68a" stop-opacity="0.65"/>
      <stop offset="100%" stop-color="#fde68a" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1200" height="675" fill="url(#bg)"/>
  <rect width="1200" height="675" fill="url(#glow)"/>
  <rect x="90" y="90" width="1020" height="495" rx="44" fill="#020617" opacity="0.42" stroke="#67e8f9" stroke-opacity="0.28"/>
  <circle cx="885" cy="265" r="138" fill="#f3d6bf" opacity="0.95"/>
  <circle cx="845" cy="242" r="16" fill="#2f1725"/>
  <circle cx="922" cy="242" r="16" fill="#2f1725"/>
  <path d="M832 318 Q884 356 936 318" stroke="#2f1725" stroke-width="11" fill="none" stroke-linecap="round"/>
  <rect x="780" y="426" width="218" height="120" rx="60" fill="#d6b39a" opacity="0.9"/>
  <rect x="150" y="160" width="260" height="310" rx="36" fill="#fff7ed" opacity="0.92"/>
  <rect x="205" y="215" width="150" height="200" rx="28" fill="#f4c7ab" opacity="0.9"/>
  <text x="140" y="130" fill="#67e8f9" font-family="Arial" font-size="25" font-weight="900">{safe_label}</text>
  <text x="470" y="150" fill="#ffffff" font-family="Arial" font-size="44" font-weight="900">Generated Creative Visual</text>
  <text x="470" y="202" fill="#dbeafe" font-family="Arial" font-size="23">Provider fallback preview asset</text>
  <foreignObject x="470" y="250" width="520" height="190">
    <div xmlns="http://www.w3.org/1999/xhtml" style="font-family:Arial;color:#e2e8f0;font-size:22px;line-height:1.38;">
      {safe_prompt}
    </div>
  </foreignObject>
  <text x="470" y="540" fill="#fef3c7" font-family="Arial" font-size="21" font-weight="800">Asset ID: {asset_id}</text>
</svg>
""".strip()

    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def generate_creative_visual_asset(
    *,
    prompt: str,
    agent_id: str = "creative_agent",
    tenant_id: str = "owner_admin",
    asset_kind: str = "creative_visual_asset",
) -> Dict[str, Any]:
    asset_id = f"creative_asset_{uuid.uuid4().hex[:10]}"
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    profile = _profile_for_agent(agent_id)

    openai_key_present = bool(os.getenv("OPENAI_API_KEY", "").strip())

    if OpenAI and openai_key_present:
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            image_prompt = f"""
Create a premium, commercially usable visual asset.

Agent profile:
{profile["label"]}

Creative direction:
{profile["prompt_style"]}

Business/task context:
{prompt}

Requirements:
- premium SaaS/client-ready quality
- clean composition
- no fake UI text unless visually necessary
- no exaggerated medical claims
- no logos unless supplied
- realistic, polished, high-conversion creative
"""

            result = client.images.generate(
                model="gpt-image-1",
                prompt=image_prompt,
                size="1536x1024",
            )

            image_b64 = result.data[0].b64_json
            data_url = f"data:image/png;base64,{image_b64}"

            return {
                "success": True,
                "asset_id": asset_id,
                "asset_url": data_url,
                "preview_url": data_url,
                "media_url": data_url,
                "generated_files": [],
                "provider": "openai_gpt_image_1",
                "generation_type": asset_kind,
                "agent_id": agent_id,
                "provider_live_generation": True,
                "fallback_used": False,
                "created_at": timestamp,
            }
        except Exception as e:
            fallback_url = _fallback_svg(prompt, asset_id, agent_id)
            return {
                "success": True,
                "asset_id": asset_id,
                "asset_url": fallback_url,
                "preview_url": fallback_url,
                "media_url": fallback_url,
                "generated_files": [],
                "provider": "svg_fallback_after_provider_failure",
                "generation_type": asset_kind,
                "agent_id": agent_id,
                "provider_live_generation": False,
                "fallback_used": True,
                "provider_error": str(e),
                "created_at": timestamp,
            }

    fallback_url = _fallback_svg(prompt, asset_id, agent_id)
    return {
        "success": True,
        "asset_id": asset_id,
        "asset_url": fallback_url,
        "preview_url": fallback_url,
        "media_url": fallback_url,
        "generated_files": [],
        "provider": "local_visual_generation_runtime",
        "generation_type": asset_kind,
        "agent_id": agent_id,
        "provider_live_generation": False,
        "fallback_used": True,
        "created_at": timestamp,
    }


def generate_ugc_visual_asset(prompt: str, tenant_id: str = "owner_admin"):
    return generate_creative_visual_asset(
        prompt=prompt,
        agent_id="ugc_creative_agent",
        tenant_id=tenant_id,
        asset_kind="ugc_visual_asset",
    )
''', encoding="utf-8")

print("SHARED_CREATIVE_VISUAL_RUNTIME_INSTALLED")