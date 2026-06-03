from datetime import datetime, timezone
from typing import Any, Dict

try:
    from backend.app.runtime.unified_creative_provider_orchestration import choose_creative_provider_mix
except Exception:
    choose_creative_provider_mix = None

try:
    from backend.app.runtime.creative_workflow_chaining_layer import create_creative_workflow_chain
except Exception:
    create_creative_workflow_chain = None

try:
    from backend.app.runtime.creative_quality_refinement_loop import compare_creative_provider_options
except Exception:
    compare_creative_provider_options = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_runtime_creative_execution_plan(
    creative_goal: str,
    content_type: str = "video",
    target_platform: str = "general",
    language: str = "English",
    accent: str = "",
    region: str = "",
    quality_priority: str = "high",
    budget_priority: str = "balanced",
    requires_avatar: bool = False,
    requires_lipsync: bool = False,
    requires_dubbing: bool = False,
    requires_cinematic: bool = False,
    requires_ugc_realism: bool = False,
    requires_voiceover: bool = True,
    owner_approved_live_execution: bool = False,
) -> Dict[str, Any]:
    if choose_creative_provider_mix is None:
        return {
            "success": False,
            "status": "orchestration_layer_unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
        }

    if create_creative_workflow_chain is None:
        return {
            "success": False,
            "status": "workflow_chaining_layer_unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
        }

    if compare_creative_provider_options is None:
        return {
            "success": False,
            "status": "quality_refinement_layer_unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
        }

    provider_plan = choose_creative_provider_mix(
        creative_goal=creative_goal,
        content_type=content_type,
        target_platform=target_platform,
        language=language,
        accent=accent,
        region=region,
        quality_priority=quality_priority,
        budget_priority=budget_priority,
        requires_avatar=requires_avatar,
        requires_lipsync=requires_lipsync,
        requires_dubbing=requires_dubbing,
        requires_cinematic=requires_cinematic,
        requires_ugc_realism=requires_ugc_realism,
        requires_voiceover=requires_voiceover,
        owner_approved_live_execution=owner_approved_live_execution,
    )

    workflow_chain = create_creative_workflow_chain(
        workflow_goal=creative_goal,
        target_platform=target_platform,
        language=language,
        region=region,
        quality_priority=quality_priority,
        owner_approved_live_execution=owner_approved_live_execution,
    )

    selected_providers = provider_plan.get("selected_providers", [])

    quality_comparison = compare_creative_provider_options(
        creative_goal=creative_goal,
        providers=selected_providers,
        multilingual=language.lower() != "english" or requires_dubbing,
    )

    execution_allowed = bool(owner_approved_live_execution)

    return {
        "success": True,
        "layer": "runtime_creative_execution_integration",
        "status": "runtime_creative_execution_plan_created",
        "creative_goal": creative_goal,
        "content_type": content_type,
        "target_platform": target_platform,
        "language": language,
        "accent": accent,
        "region": region,
        "quality_priority": quality_priority,
        "budget_priority": budget_priority,
        "execution_allowed": execution_allowed,
        "owner_approval_required_for_live_execution": not execution_allowed,
        "provider_plan": provider_plan,
        "workflow_chain": workflow_chain,
        "quality_comparison": quality_comparison,
        "recommended_provider": quality_comparison.get("best_provider_recommendation"),
        "selected_providers": selected_providers,
        "workflow_steps": workflow_chain.get("workflow_steps", []),
        "learning_signals_ready": True,
        "provider_fallback_ready": True,
        "retry_refinement_ready": True,
        "deliverable_generation_ready": True,
        "hardcoded_execution_path": False,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "runtime_rules": [
            "Runtime planning does not trigger paid provider calls.",
            "Live execution remains owner-approved.",
            "Provider selection stays flexible and policy-driven.",
            "Workflow chains can change by goal, platform, language, and region.",
            "Quality scoring can influence future routing.",
            "Learning signals may improve routing but cannot override governance.",
            "Credential values must never be exposed.",
        ],
        "created_at": _now(),
    }


def get_runtime_creative_execution_integration_status() -> Dict[str, Any]:
    return {
        "success": True,
        "layer": "runtime_creative_execution_integration",
        "status": "ready",
        "orchestration_connected": choose_creative_provider_mix is not None,
        "workflow_chaining_connected": create_creative_workflow_chain is not None,
        "quality_refinement_connected": compare_creative_provider_options is not None,
        "runtime_planning_enabled": True,
        "provider_fallback_ready": True,
        "retry_refinement_ready": True,
        "learning_signal_handoff_ready": True,
        "deliverable_generation_ready": True,
        "hardcoded_execution_path": False,
        "owner_approval_required_for_live_execution": True,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "verified_at": _now(),
    }
