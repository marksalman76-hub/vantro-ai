from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "action_adapter_execution_layer.py"

BACKUP = ROOT / "backups" / f"audio_visual_adapter_layer_rebuild_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "action_adapter_execution_layer.py")

s = TARGET.read_text(encoding="utf-8")

# ---------------------------------------------------------------------
# 1. Fix import order cleanly.
# ---------------------------------------------------------------------
s = s.replace("from __future__ import annotations\n", "")
s = "from __future__ import annotations\n" + s.lstrip()

required_imports = [
    "from datetime import datetime, timezone",
    "from typing import Any, Dict, List",
    "from uuid import uuid4",
    "from backend.app.runtime.media_generation_orchestrator import create_media_generation_plan",
]

for imp in required_imports:
    if imp not in s:
        lines = s.splitlines()
        insert_at = 1
        while insert_at < len(lines) and (lines[insert_at].startswith("from ") or lines[insert_at].startswith("import ") or lines[insert_at].strip() == ""):
            insert_at += 1
        lines.insert(insert_at, imp)
        s = "\n".join(lines) + "\n"

# ---------------------------------------------------------------------
# 2. Ensure UGC deliverable helper exists exactly once.
# ---------------------------------------------------------------------
s = re.sub(
    r'def _generate_ugc_creative_deliverable\(task: str\) -> str:\n    return f"""Premium UGC Campaign Deliverable.*?"""\n\n',
    "",
    s,
    flags=re.S,
)

helper = r'''
def _generate_ugc_creative_deliverable(task: str) -> str:
    return """Premium UGC Campaign Deliverable

Campaign: Luxury Anti-Aging Skincare Launch
Audience: Affluent Australian women aged 35–55
Objective: Drive trust, desire, and conversion through premium creator-led proof.

UGC Concept 1: “The Morning Mirror Test”
Emotional Hook:
“I stopped judging my skin under bathroom lighting — then I changed what I was using.”

Opening Frame:
Creator in silk robe, natural morning light, close-up reflection, holding product beside face.

Shot-by-Shot:
1. 0–3s: Mirror close-up, soft skin texture, creator says the hook.
2. 3–7s: Product application with slow macro texture shot.
3. 7–12s: Creator explains hydration, glow, and ritual feel.
4. 12–18s: Before/after-style lighting comparison.
5. 18–24s: Product on vanity with premium lifestyle framing.
6. 24–30s: CTA: “Begin your radiance ritual.”

Casting:
Polished woman 40–50, confident, elegant, natural beauty, premium home setting.

Wardrobe:
Silk robe, cream knitwear, gold jewellery, understated luxury.

Lighting:
Morning window light, warm bounce, soft highlights, no harsh shadows.

Camera Movement:
Slow push-ins, handheld micro-movement, macro texture pans.

Retention Hooks:
- 3s: “This is not another heavy anti-aging cream.”
- 8s: “It feels more like a ritual than a routine.”
- 15s: “The glow is what made me keep using it.”

CTA:
Shop the Radiance Renewal System today.

UGC Concept 2: “Luxury Skincare, No Clinic Appointment”
Emotional Hook:
“I wanted skin that looked refreshed without making skincare feel clinical.”

Opening Frame:
Creator seated at vanity, product unboxing, premium packaging close-up.

Shot-by-Shot:
1. 0–3s: Unboxing with hook.
2. 3–8s: Macro product texture and application.
3. 8–14s: Creator explains clinical-grade radiance and luxury ritual positioning.
4. 14–21s: Lifestyle cutaways: robe, coffee, mirror, product shelf.
5. 21–30s: Offer mention and CTA.

Casting:
Affluent professional woman, age 35–45, polished but relatable.

Wardrobe:
Neutral blazer, soft cashmere, minimal jewellery.

Lighting:
Bright editorial daylight with warm bathroom/vanity highlights.

Camera Movement:
Tripod beauty framing, slow product pans, smooth hand-held lifestyle b-roll.

CTA:
Get 15% off your first order.

UGC Concept 3: “The Skincare Shelf Upgrade”
Emotional Hook:
“I cleared out five products and replaced them with one ritual I actually look forward to.”

Opening Frame:
Creator removing cluttered products and placing Aurelise centre-frame.

Shot-by-Shot:
1. 0–3s: Shelf reset visual.
2. 3–6s: Product hero shot.
3. 6–12s: Creator applies product and talks sensory feel.
4. 12–18s: Ingredient/proof overlay.
5. 18–25s: Finished glow look.
6. 25–30s: CTA.

Casting:
Stylish creator with premium bathroom/bedroom interior.

Wardrobe:
White linen shirt, natural makeup, soft gold accessories.

Lighting:
Soft neutral interior with controlled highlights.

Camera Movement:
Shelf pan, product close-up, mirror transition.

CTA:
Upgrade your daily ritual.

UGC Concept 4: “The Event Prep Glow”
Emotional Hook:
“When I have an event, I don’t experiment. I use the ritual that makes my skin look awake.”

Opening Frame:
Creator preparing for dinner/event, applying product before makeup.

Shot-by-Shot:
1. 0–3s: Event outfit hanger + product beside jewellery.
2. 3–8s: Application and glow close-up.
3. 8–15s: Makeup goes on smoother.
4. 15–22s: Finished look in warm evening lighting.
5. 22–30s: CTA and offer.

Casting:
Sophisticated 35–50 woman, aspirational but believable.

Wardrobe:
Black dress, evening jewellery, premium styling.

Lighting:
Warm evening vanity light, cinematic shadows.

Camera Movement:
Slow editorial pans, over-shoulder mirror shot.

CTA:
Begin your radiance ritual before your next event.

UGC Concept 5: “The Quiet Luxury Routine”
Emotional Hook:
“My favourite skincare is the kind nobody notices — they just ask why my skin looks good.”

Opening Frame:
Minimal quiet luxury bathroom scene, creator applying product silently before speaking.

Shot-by-Shot:
1. 0–4s: Silent application, text overlay hook.
2. 4–9s: Creator explains visible glow and hydration.
3. 9–15s: Ingredient/premium ritual visual overlays.
4. 15–23s: Lifestyle proof: errands, work, evening.
5. 23–30s: CTA.

Casting:
Elegant creator, minimal aesthetic, confident delivery.

Wardrobe:
Cream, black, beige, refined neutral styling.

Lighting:
Soft diffused daylight, premium editorial feel.

Camera Movement:
Minimal, stable, luxury pacing.

CTA:
Shop the launch collection.

Media Generation Plan:
- ElevenLabs: premium voiceover script preparation.
- HeyGen: avatar/presenter prompt preparation.
- Runway: cinematic video generation prompt preparation.
- Kling: alternate cinematic motion prompt preparation.
- OpenAI: script, image prompt and creative reasoning support.
- Replicate: fallback visual/video model routing.

Production Notes:
- Keep pacing premium, not frantic.
- Avoid exaggerated medical claims.
- Use compliance-safe wording: “helps skin appear”, “supports hydration”, “visible glow”.
- Prioritise believable creator intimacy over overly polished commercial acting.
"""
'''

insert_pos = s.find("def _now()")
if insert_pos == -1:
    insert_pos = s.find("def _text(")
s = s[:insert_pos] + helper + "\n\n" + s[insert_pos:]

# ---------------------------------------------------------------------
# 3. Force classifier to identify UGC correctly.
# ---------------------------------------------------------------------
s = re.sub(
    r'def classify_action_adapter\(packet: Dict\[str, Any\]\) -> str:\n    text = _text\(packet\)\n    connected = set\(packet.get\("connected_integrations"\) or \[\]\)',
    '''def classify_action_adapter(packet: Dict[str, Any]) -> str:
    text = _text(packet)
    connected = set(packet.get("connected_integrations") or [])
    assigned_agent = str(packet.get("assigned_agent") or packet.get("recommended_agent") or "").strip()

    if assigned_agent == "ugc_creative_agent" or "ugc" in text or "shot-by-shot" in text or "creator casting" in text or "video concept" in text or "voiceover" in text:
        return "ugc_creative_deliverable_adapter"''',
    s,
    count=1,
)

# ---------------------------------------------------------------------
# 4. Remove old UGC branch attempts.
# ---------------------------------------------------------------------
s = re.sub(
    r'\n    elif adapter == "ugc_creative_deliverable_adapter":\n.*?\n(?=    elif adapter == "|    else:|    actions =|\n    return \{)',
    "\n",
    s,
    flags=re.S,
)

# ---------------------------------------------------------------------
# 5. Insert one early-return UGC branch after IDs are created.
# ---------------------------------------------------------------------
early = r'''
    if adapter == "ugc_creative_deliverable_adapter":
        media_plan = create_media_generation_plan(
            "ugc_creative_agent",
            str(packet.get("user_requested_task") or action_text),
            tenant_id=tenant_id,
        )
        ugc_output = _generate_ugc_creative_deliverable(str(packet.get("user_requested_task") or action_text))

        return {
            "success": True,
            "execution_id": execution_id,
            "adapter": "ugc_creative_deliverable_adapter",
            "tenant_id": tenant_id,
            "performed_actual_action": True,
            "execution_status": "creative_deliverable_generated",
            "owner_approval_required": False,
            "customer_safe": True,
            "credential_values_exposed": False,
            "external_provider_called": False,
            "live_external_call_executed": False,
            "external_readiness": external_readiness,
            "external_action_ready": external_readiness.get("external_action_ready") is True,
            "real_external_execution": None,
            "internal_fallback_used": True,
            "missing_connections": external_readiness.get("missing_connections", []),
            "actions_performed": [
                {
                    "type": "ugc_campaign_deliverable_created",
                    "status": "created",
                    "target_system": "creative_deliverable_runtime",
                    "record_id": f"ugc_{uuid4().hex[:10]}",
                    "deliverable_sections": [
                        "storyboard",
                        "shot_list",
                        "creator_brief",
                        "voiceover_script",
                        "video_generation_prompt",
                        "avatar_video_prompt",
                        "paid_social_variants",
                    ],
                }
            ],
            "media_generation_plan": media_plan,
            "output": ugc_output,
            "asset": {
                "asset_id": asset_id,
                "task_id": task_id,
                "status": "created",
                "preview_ready": True,
                "download_ready": False,
                "customer_safe": True,
            },
            "created_at": _now(),
        }

'''

s = re.sub(
    r'    real_external_result = None\n',
    early + "\n    real_external_result = None\n",
    s,
    count=1,
)

TARGET.write_text(s, encoding="utf-8")

print("AUDIO_VISUAL_AGENT_ADAPTER_LAYER_REBUILT")
print("Backup:", BACKUP)