"""
Ecommerce AI Agent Platform API Runtime

Executable FastAPI backend for the global white-label ecommerce agent system.
Includes tenant enforcement, agent entitlement, AI generation, owner approval,
premium quality gate, output polish layer, JSON memory persistence,
SQLite production persistence, learning recommendations,
behaviour optimisation, and execution stack routing.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List

from backend.app.agents.agent_registry import agent_exists
from backend.app.approval.owner_approval_gateway import (
    OwnerApprovalGateway,
    approval_summary,
)
from backend.app.core.ai_generation_service import (
    AIGenerationService,
    GenerationRequest,
)
from backend.app.quality.output_polish_layer import OutputPolishLayer
from backend.app.quality.premium_quality_gate import (
    PremiumQualityGate,
    quality_summary,
)
from backend.app.runtime.behaviour_optimisation_memory import (
    BehaviourOptimisationMemory,
    behaviour_optimisation_summary,
)
from backend.app.runtime.execution_stack import (
    ExecutionRequest,
    ExecutionStack,
    execution_summary,
)
from backend.app.runtime.learning_recommendation_engine import (
    LearningRecommendationEngine,
    learning_recommendation_summary,
)
from backend.app.runtime.memory_store import MemoryStore
from backend.app.runtime.sqlite_store import SQLiteStore
from backend.app.workflows.ecommerce_workflow_engine import (
    EcommerceWorkflowEngine,
    workflow_summary,
)


app = FastAPI(
    title="Ecommerce AI Agent Platform",
    version="1.1.0",
)


DEMO_TENANTS: Dict[str, List[str]] = {
    "client_demo_001": [
        "master_orchestrator_agent",
        "ugc_creative_agent",
        "analytics_optimisation_agent",
        "product_research_agent",
        "ad_creative_agent",
        "product_image_direction_agent",
        "influencer_collaboration_agent",
    ]
}


ACTION_TO_EXECUTION_MAP: Dict[str, str] = {
    "ugc_script_generation": "create_ugc_video_brief",
    "product_image_generation": "create_product_image_brief",
    "product_image_direction": "create_product_image_brief",
    "ad_copy_generation": "create_ad_copy_brief",
    "website_content_generation": "create_landing_page_brief",
    "product_copy_generation": "create_shopify_product_page",
    "influencer_shortlist": "prepare_influencer_outreach",
    "influencer_outreach_draft": "prepare_influencer_outreach",
    "customer_support_reply": "prepare_customer_support_reply",
    "analytics_report": "prepare_analytics_report",
    "scale_campaign": "scale_campaign",
    "launch_paid_campaign": "launch_paid_campaign",
    "increase_ad_spend": "increase_ad_spend",
    "change_campaign_budget": "change_campaign_budget",
    "paid_influencer_collaboration": "paid_influencer_collaboration",
    "commission_agreement": "commission_agreement",
    "usage_rights_contract": "usage_rights_contract",
    "large_supplier_order": "large_supplier_order",
    "large_refund_batch": "large_refund_batch",
    "major_strategy_change": "major_strategy_change",
}


class HealthResponse(BaseModel):
    success: bool
    system: str
    status: str
    global_ready: bool
    white_label_ready: bool
    owner_approval_required_for_spend: bool
    generation_layer: str
    execution_stack: str
    polish_layer: str
    memory_layer: str
    sqlite_layer: str
    learning_layer: str
    behaviour_optimisation_layer: str


class RunAgentRequest(BaseModel):
    tenant_id: str
    requested_agent: str
    workflow_stage: str
    task: str
    action_type: str
    region: str = "Global"
    language: str = "English"
    currency: str = "USD"
    owner_approved: bool = False
    execute_real_world_action: bool = True
    project_id: str = "default_project"


@app.get("/health", response_model=HealthResponse)
def health() -> Dict[str, object]:
    return {
        "success": True,
        "system": "premium_global_white_label_ecommerce_ai_agent_platform",
        "status": "running",
        "global_ready": True,
        "white_label_ready": True,
        "owner_approval_required_for_spend": True,
        "generation_layer": "ai_generation_service",
        "execution_stack": "enabled",
        "polish_layer": "enabled",
        "memory_layer": "enabled",
        "sqlite_layer": "enabled",
        "learning_layer": "enabled",
        "behaviour_optimisation_layer": "enabled",
    }


@app.post("/run-agent")
def run_agent(request: RunAgentRequest) -> Dict[str, object]:
    if request.tenant_id not in DEMO_TENANTS:
        return {
            "success": False,
            "error": "tenant_not_found_or_not_active",
            "tenant_id": request.tenant_id,
        }

    if not agent_exists(request.requested_agent):
        return {
            "success": False,
            "error": "unknown_agent",
            "requested_agent": request.requested_agent,
        }

    if request.requested_agent not in DEMO_TENANTS[request.tenant_id]:
        return {
            "success": False,
            "error": "agent_not_active_for_tenant",
            "tenant_id": request.tenant_id,
            "requested_agent": request.requested_agent,
        }

    workflow_engine = EcommerceWorkflowEngine()
    approval_gateway = OwnerApprovalGateway()
    quality_gate = PremiumQualityGate()
    generation_service = AIGenerationService()
    polish_layer = OutputPolishLayer()
    execution_stack = ExecutionStack()

    memory_store = MemoryStore()
    sqlite_store = SQLiteStore()

    learning_engine = LearningRecommendationEngine()
    behaviour_engine = BehaviourOptimisationMemory()

    workflow_packet = workflow_engine.create_packet(
        tenant_id=request.tenant_id,
        workflow_stage=request.workflow_stage,
        requested_agent=request.requested_agent,
        task=request.task,
        region=request.region,
        language=request.language,
        currency=request.currency,
    )

    approval_decision = approval_gateway.evaluate_action(
        action_type=request.action_type,
        owner_approved=request.owner_approved,
    )

    if not approval_decision.approved:
        blocked_payload = {
            "workflow": workflow_summary(workflow_packet),
            "approval": approval_summary(approval_decision),
        }

        memory_store.add_record(
            tenant_id=request.tenant_id,
            project_id=request.project_id,
            record_type="blocked_execution",
            title=f"Blocked action: {request.action_type}",
            payload=blocked_payload,
        )

        sqlite_store.add_record(
            tenant_id=request.tenant_id,
            project_id=request.project_id,
            record_type="blocked_execution",
            title=f"Blocked action: {request.action_type}",
            payload=blocked_payload,
        )

        return {
            "success": False,
            "status": approval_decision.status,
            "workflow": workflow_summary(workflow_packet),
            "approval": approval_summary(approval_decision),
            "message": "Action paused or rejected by owner approval gateway.",
        }

    generation_request = GenerationRequest(
        tenant_id=request.tenant_id,
        requested_agent=request.requested_agent,
        workflow_stage=request.workflow_stage,
        task=request.task,
        region=request.region,
        language=request.language,
        currency=request.currency,
    )

    generated_output = generation_service.generate(generation_request)

    polished_output = polish_layer.polish_output(generated_output)

    quality_result = quality_gate.review_output(polished_output)

    if not quality_result.passed:
        quality_failure_payload = {
            "workflow": workflow_summary(workflow_packet),
            "quality": quality_summary(quality_result),
            "output": polished_output,
        }

        memory_store.add_record(
            tenant_id=request.tenant_id,
            project_id=request.project_id,
            record_type="quality_gate_failure",
            title="Premium quality gate rejection",
            payload=quality_failure_payload,
        )

        sqlite_store.add_record(
            tenant_id=request.tenant_id,
            project_id=request.project_id,
            record_type="quality_gate_failure",
            title="Premium quality gate rejection",
            payload=quality_failure_payload,
        )

        return {
            "success": False,
            "status": "quality_gate_failed",
            "workflow": workflow_summary(workflow_packet),
            "quality": quality_summary(quality_result),
            "message": "Output rejected by premium quality gate.",
        }

    execution_action = ACTION_TO_EXECUTION_MAP.get(
        request.action_type,
        request.action_type,
    )

    execution_result = None

    if request.execute_real_world_action:
        execution_result = execution_stack.route(
            ExecutionRequest(
                tenant_id=request.tenant_id,
                action_type=execution_action,
                payload={
                    "workflow": workflow_summary(workflow_packet),
                    "approval": approval_summary(approval_decision),
                    "quality": quality_summary(quality_result),
                    "output": polished_output,
                },
                owner_approved=approval_decision.approved,
                quality_passed=quality_result.passed,
            )
        )

    successful_payload = {
        "workflow": workflow_summary(workflow_packet),
        "approval": approval_summary(approval_decision),
        "quality": quality_summary(quality_result),
        "execution": execution_summary(execution_result)
        if execution_result
        else None,
        "output": polished_output,
    }

    memory_store.add_record(
        tenant_id=request.tenant_id,
        project_id=request.project_id,
        record_type="successful_execution",
        title=f"{request.requested_agent} execution",
        payload=successful_payload,
    )

    sqlite_store.add_record(
        tenant_id=request.tenant_id,
        project_id=request.project_id,
        record_type="successful_execution",
        title=f"{request.requested_agent} execution",
        payload=successful_payload,
    )

    latest_execution_memory = memory_store.latest_record(
        tenant_id=request.tenant_id,
        project_id=request.project_id,
        record_type="successful_execution",
    )

    latest_sqlite_record = sqlite_store.latest_record(
        tenant_id=request.tenant_id,
        project_id=request.project_id,
        record_type="successful_execution",
    )

    learning_recommendations = learning_engine.generate_recommendations(
        tenant_id=request.tenant_id,
        project_id=request.project_id,
    )

    behaviour_optimisation = behaviour_engine.analyse_project(
        tenant_id=request.tenant_id,
        project_id=request.project_id,
    )

    return {
        "success": True,
        "status": "agent_execution_completed",
        "workflow": workflow_summary(workflow_packet),
        "approval": approval_summary(approval_decision),
        "quality": quality_summary(quality_result),
        "execution": execution_summary(execution_result)
        if execution_result
        else None,
        "memory": {
            "memory_saved": True,
            "latest_memory_id": latest_execution_memory.get("memory_id")
            if latest_execution_memory
            else None,
        },
        "sqlite": {
            "sqlite_saved": True,
            "latest_sqlite_record_id": latest_sqlite_record.get("record_id")
            if latest_sqlite_record
            else None,
        },
        "learning": learning_recommendation_summary(
            learning_recommendations
        ),
        "behaviour_optimisation": behaviour_optimisation_summary(
            behaviour_optimisation
        ),
        "output": polished_output,
    }

# Step 69 — Provider Execution Audit Admin Visibility Route
try:
    from backend.app.core.provider_execution_audit_log import provider_execution_audit_log
except Exception:
    provider_execution_audit_log = None


@app.get("/admin/provider-execution-audit")
def admin_provider_execution_audit(limit: int = 20):
    """
    Admin-safe provider execution audit visibility.

    Does not expose:
    - provider credential values
    - internal prompts
    - backend configuration
    - learning internals
    - governance internals
    """
    if provider_execution_audit_log is None:
        return {
            "success": False,
            "error": "provider_execution_audit_log_unavailable",
            "client_safe": True,
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
        }

    safe_limit = max(1, min(int(limit), 100))
    latest = provider_execution_audit_log.latest(safe_limit)

    return {
        "success": True,
        "route": "/admin/provider-execution-audit",
        "events": latest.get("events", []),
        "count": latest.get("count", 0),
        "limit": safe_limit,
        "visibility": {
            "admin_only": True,
            "client_safe": True,
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "learning_internals_exposed": False,
        },
    }

# Step 70 — Provider Credential Readiness Admin Route
try:
    from backend.app.core.llm_provider_credential_readiness import (
        LLMProviderCredentialReadiness,
    )
except Exception:
    LLMProviderCredentialReadiness = None


@app.get("/admin/provider-readiness")
def admin_provider_readiness():
    """
    Admin-safe provider readiness visibility.

    This route shows provider readiness only.
    It never exposes credential values, secrets, prompts, backend configuration,
    or learning/governance internals.
    """
    if LLMProviderCredentialReadiness is None:
        return {
            "success": False,
            "error": "provider_credential_readiness_unavailable",
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "client_safe": True,
        }

    readiness = LLMProviderCredentialReadiness().check_all()

    return {
        "success": True,
        "route": "/admin/provider-readiness",
        "readiness": readiness,
        "visibility": {
            "admin_only": True,
            "client_safe": True,
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "learning_internals_exposed": False,
            "governance_internals_exposed": False,
        },
    }

# Step 77 — Owner Live LLM Admin Control Routes
try:
    from backend.app.core.owner_live_llm_control import owner_live_llm_control
except Exception:
    owner_live_llm_control = None


@app.get("/admin/live-llm-control")
def admin_get_live_llm_control():
    if owner_live_llm_control is None:
        return {
            "success": False,
            "error": "owner_live_llm_control_unavailable",
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "client_safe": True,
        }

    return {
        "success": True,
        "route": "/admin/live-llm-control",
        "state": owner_live_llm_control.get_state(),
        "visibility": {
            "admin_only": True,
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "learning_internals_exposed": False,
            "governance_internals_exposed": False,
            "client_safe": True,
        },
    }


@app.post("/admin/live-llm-control")
def admin_set_live_llm_control(payload: dict):
    if owner_live_llm_control is None:
        return {
            "success": False,
            "error": "owner_live_llm_control_unavailable",
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "client_safe": True,
        }

    enabled = bool(payload.get("enabled", False))
    updated_by = str(payload.get("updated_by", "owner"))
    reason = str(payload.get("reason", ""))

    result = owner_live_llm_control.set_state(
        enabled=enabled,
        updated_by=updated_by,
        reason=reason,
    )

    return {
        "success": True,
        "route": "/admin/live-llm-control",
        "result": result,
        "visibility": {
            "admin_only": True,
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "learning_internals_exposed": False,
            "governance_internals_exposed": False,
            "client_safe": True,
        },
    }

# Step 82 — OpenAI SDK Admin Readiness Route
try:
    from backend.app.core.openai_sdk_dependency_guard import openai_sdk_dependency_guard
except Exception:
    openai_sdk_dependency_guard = None


@app.get("/admin/openai-sdk-readiness")
def admin_openai_sdk_readiness():
    if openai_sdk_dependency_guard is None:
        return {
            "success": False,
            "error": "openai_sdk_dependency_guard_unavailable",
            "live_call_attempted": False,
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "client_safe": True,
        }

    return {
        "success": True,
        "route": "/admin/openai-sdk-readiness",
        "readiness": openai_sdk_dependency_guard.check(),
        "visibility": {
            "admin_only": True,
            "live_call_attempted": False,
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "client_safe": True,
        },
    }

# Step 83 — Full Live LLM Readiness Dashboard Route
@app.get("/admin/live-llm-readiness-dashboard")
def admin_live_llm_readiness_dashboard():
    credential_readiness = None
    sdk_readiness = None
    owner_control_state = None

    try:
        from backend.app.core.llm_provider_credential_readiness import LLMProviderCredentialReadiness
        credential_readiness = LLMProviderCredentialReadiness().check_all()
    except Exception:
        credential_readiness = {
            "success": False,
            "error": "credential_readiness_unavailable",
            "credential_values_exposed": False,
        }

    try:
        from backend.app.core.openai_sdk_dependency_guard import openai_sdk_dependency_guard
        sdk_readiness = openai_sdk_dependency_guard.check()
    except Exception:
        sdk_readiness = {
            "success": False,
            "error": "openai_sdk_guard_unavailable",
            "live_call_attempted": False,
            "credential_values_exposed": False,
        }

    try:
        from backend.app.core.owner_live_llm_control import owner_live_llm_control
        owner_control_state = owner_live_llm_control.get_state()
    except Exception:
        owner_control_state = {
            "live_llm_execution_enabled": False,
            "error": "owner_live_llm_control_unavailable",
            "credential_values_stored": False,
        }

    ready_checks = {
        "provider_credentials_configured": bool(
            credential_readiness.get("live_provider_execution_ready", False)
        ),
        "openai_sdk_installed": bool(sdk_readiness.get("installed", False)),
        "owner_live_control_enabled": bool(
            owner_control_state.get("live_llm_execution_enabled", False)
        ),
        "credential_values_hidden": credential_readiness.get("credential_values_exposed", False) is False,
        "sdk_no_live_call_attempted": sdk_readiness.get("live_call_attempted", False) is False,
        "owner_control_no_credentials_stored": owner_control_state.get("credential_values_stored", False) is False,
    }

    live_ready = all(ready_checks.values())

    return {
        "success": True,
        "route": "/admin/live-llm-readiness-dashboard",
        "live_llm_execution_ready": live_ready,
        "execution_mode": (
            "live_llm_ready_pending_global_env_flag"
            if live_ready
            else "live_llm_not_ready"
        ),
        "ready_checks": ready_checks,
        "credential_readiness": credential_readiness,
        "sdk_readiness": sdk_readiness,
        "owner_control": owner_control_state,
        "visibility": {
            "admin_only": True,
            "live_call_attempted": False,
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "learning_internals_exposed": False,
            "governance_internals_exposed": False,
            "client_safe": True,
        },
    }

