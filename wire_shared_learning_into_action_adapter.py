from pathlib import Path

p = Path("backend/app/runtime/action_adapter_execution_layer.py")
text = p.read_text(encoding="utf-8")

if "from backend.app.runtime.shared_agent_learning_runtime import" not in text:
    text = text.replace(
        "from backend.app.runtime.shared_creative_media_generation_runtime import generate_creative_media_pack\n",
        "from backend.app.runtime.shared_creative_media_generation_runtime import generate_creative_media_pack\nfrom backend.app.runtime.shared_agent_learning_runtime import load_agent_learning_context, save_agent_learning, hide_proprietary_learning_fields\n",
        1,
    )

anchor = '''    action_text = (
        packet.get("implementation_action")
        or packet.get("action")
        or packet.get("title")
        or packet.get("description")
        or "Approved operational task"
    )
'''

replacement = '''    action_text = (
        packet.get("implementation_action")
        or packet.get("action")
        or packet.get("title")
        or packet.get("description")
        or "Approved operational task"
    )

    learning_context = load_agent_learning_context(
        tenant_id=tenant_id,
        agent_id=str(packet.get("assigned_agent") or packet.get("agent") or packet.get("recommended_agent") or "unknown_agent"),
        task=str(packet.get("user_requested_task") or action_text),
    )
'''

if anchor not in text:
    raise SystemExit("action_text anchor not found")

text = text.replace(anchor, replacement, 1)

anchor2 = '''    visual_generated_files = visual_asset.get("generated_files", []) if visual_asset else []
    visual_provider = visual_asset.get("provider") if visual_asset else None
    visual_provider_live_generation = visual_asset.get("provider_live_generation") if visual_asset else False
    visual_fallback_used = visual_asset.get("fallback_used") if visual_asset else False
    media_pack_payload = media_pack or {}
'''

replacement2 = '''    visual_generated_files = visual_asset.get("generated_files", []) if visual_asset else []
    visual_provider = visual_asset.get("provider") if visual_asset else None
    visual_provider_live_generation = visual_asset.get("provider_live_generation") if visual_asset else False
    visual_fallback_used = visual_asset.get("fallback_used") if visual_asset else False
    media_pack_payload = media_pack or {}

    learning_saved_packet = save_agent_learning(
        tenant_id=tenant_id,
        agent_id=str(packet.get("assigned_agent") or packet.get("agent") or packet.get("recommended_agent") or "unknown_agent"),
        task=str(packet.get("user_requested_task") or action_text),
        output_summary=str(output)[:1200],
        quality_score=85 if output else 60,
        approved=None,
        provider=str(visual_provider or ""),
        media_type="creative_media_pack" if media_pack_payload else "text_output",
        source="action_adapter_execution",
    )
'''

if anchor2 not in text:
    raise SystemExit("visual field anchor not found")

text = text.replace(anchor2, replacement2, 1)

anchor3 = '''        "supports_avatar_video": media_pack_payload.get("supports_avatar_video", False),
        "external_readiness": external_readiness,
'''

replacement3 = '''        "supports_avatar_video": media_pack_payload.get("supports_avatar_video", False),
        "learning_saved": learning_saved_packet.get("learning_saved", False),
        "memory_used": learning_context.get("memory_used", False),
        "previous_pattern_applied": learning_context.get("previous_pattern_applied", False),
        "improvement_applied": learning_context.get("improvement_applied", ""),
        "quality_delta": learning_context.get("quality_delta", ""),
        "next_refinement": learning_context.get("next_refinement", ""),
        "client_safe_learning_summary": learning_context.get("client_safe_learning_summary", {}),
        "proprietary_logic_hidden": True,
        "external_readiness": external_readiness,
'''

if anchor3 not in text:
    raise SystemExit("learning return anchor not found")

text = text.replace(anchor3, replacement3, 1)

p.write_text(text, encoding="utf-8")
print("SHARED_LEARNING_WIRED_INTO_ACTION_ADAPTER")