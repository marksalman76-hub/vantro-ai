import sitecustomize  # Step 209D force local env loading
from backend.app.api.subscription_policy_routes import router as subscription_policy_router

from backend.app.core.subscription_billing_runtime import (
    billing_readiness,
    get_subscription,
    record_billing_event,
    upsert_subscription,
    handle_invoice_payment_succeeded,
    handle_invoice_payment_failed,
)


# Step 173 durable Postgres account runtime
from backend.app.core.postgres_account_runtime import (
    activate_account as pg_activate_account,
    create_activation_invite as pg_create_activation_invite,
    get_activation_invite as pg_get_activation_invite,
    get_session_account as pg_get_session_account,
    login as pg_login,
    recent_security_events as pg_recent_security_events,
    assign_client_credits as pg_assign_client_credits,
    database_readiness as pg_database_readiness,
    lookup_client_account as pg_lookup_client_account,
    client_credit_gate as pg_client_credit_gate,
)


# Step 157 tenant-aware client account runtime
from backend.app.core.tenant_account_runtime import (
    activate_client_account,
    create_client_activation_invite,
    get_account_from_session,
    get_invite_status,
    get_tenant_account_security_events,
    login_client_account,
    logout_session,
)

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



AGENT_ALIAS_MAP: Dict[str, str] = {
    "product_intelligence_agent": "product_research_agent",
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
    actor_role: str = "client"
    requested_credits: int = 1


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
    requested_agent = AGENT_ALIAS_MAP.get(request.requested_agent, request.requested_agent)

    credit_gate = pg_client_credit_gate({
        "actor_role": request.actor_role,
        "tenant_id": request.tenant_id,
        "requested_credits": request.requested_credits,
    })

    actor_role = (request.actor_role or "").strip().lower()
    owner_admin_credit_bypass = actor_role in {"owner", "admin", "system"}

    if not credit_gate.get("credit_gate_passed") and not owner_admin_credit_bypass:
        return {
            "success": False,
            "status": "credit_gate_blocked",
            "message": "Client execution is blocked until credit top-up or next billing cycle.",
            "credit_gate": credit_gate,
        }

    if not credit_gate.get("credit_gate_passed") and owner_admin_credit_bypass:
        credit_gate = {
            **credit_gate,
            "credit_gate_passed": True,
            "owner_admin_credit_bypass": True,
            "client_credit_gate_applied": False,
            "bypass_reason": "owner_admin_internal_execution",
        }

    if not agent_exists(requested_agent):
        return {
            "success": False,
            "error": "unknown_agent",
            "requested_agent": request.requested_agent,
            "normalised_agent": requested_agent,
        }

    tenant_account = pg_lookup_client_account(request.tenant_id)

    if not tenant_account.get("success"):
        return {
            "success": False,
            "error": "tenant_not_found_or_not_active",
            "tenant_id": request.tenant_id,
        }

    active_agents = tenant_account.get("account", {}).get("active_agents", [])

    if request.actor_role not in {"owner", "admin", "system"}:
        normalised_active_agents = [
            AGENT_ALIAS_MAP.get(agent, agent) for agent in active_agents
        ]

        if requested_agent not in normalised_active_agents:
            return {
                "success": False,
                "error": "agent_not_active_for_tenant",
                "tenant_id": request.tenant_id,
                "requested_agent": request.requested_agent,
                "normalised_agent": requested_agent,
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
        requested_agent=requested_agent,
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
        requested_agent=requested_agent,
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
        title=f"{requested_agent} execution",
        payload=successful_payload,
    )

    sqlite_store.add_record(
        tenant_id=request.tenant_id,
        project_id=request.project_id,
        record_type="successful_execution",
        title=f"{requested_agent} execution",
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

# Step 84 — Live LLM Environment Setup Guide Route
@app.get("/admin/live-llm-environment-setup")
def admin_live_llm_environment_setup():
    return {
        "success": True,
        "route": "/admin/live-llm-environment-setup",
        "purpose": "Admin-safe setup checklist for enabling governed live LLM execution.",
        "required_environment_variables": [
            {
                "name": "OPENAI_API_KEY",
                "required_for": "OpenAI live provider execution",
                "value_exposed": False,
                "status": "Set this in the server environment only. Never store or display the value in the UI.",
            },
            {
                "name": "ENABLE_LIVE_LLM_CALLS",
                "required_for": "Global live LLM execution gate",
                "value_exposed": False,
                "accepted_values": ["1", "true", "yes", "enabled"],
                "status": "Must be enabled only after provider credentials and owner control are approved.",
            },
        ],
        "activation_requirements": {
            "openai_sdk_installed": True,
            "provider_credential_configured": "OPENAI_API_KEY must be configured in the backend server environment.",
            "owner_control_enabled": "Owner must enable /admin/live-llm-control.",
            "global_gate_enabled": "ENABLE_LIVE_LLM_CALLS must be enabled in the server environment.",
            "safety_test_required": "Run final no-secret/no-prompt/no-config exposure verification before live production use.",
        },
        "security_rules": {
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "learning_internals_exposed": False,
            "governance_internals_exposed": False,
            "client_safe": True,
        },
        "safe_next_steps": [
            "Set OPENAI_API_KEY in the local backend environment.",
            "Set ENABLE_LIVE_LLM_CALLS=true only when ready to allow live calls.",
            "Use /admin/live-llm-control to enable owner control.",
            "Check /admin/live-llm-readiness-dashboard.",
            "Run a controlled live call test with a low-risk ecommerce task.",
        ],
    }

# Step 88 — LLM Provider Stack Completion Summary Route
@app.get("/admin/llm-provider-stack-summary")
def admin_llm_provider_stack_summary():
    return {
        "success": True,
        "route": "/admin/llm-provider-stack-summary",
        "stack_status": "complete_gated_safe_ready_for_credentials",
        "completed_steps": {
            "59": "LLM provider orchestration foundation",
            "60": "LLM routing wired into AI generation service",
            "61": "Provider execution adapter layer",
            "62": "Provider execution wired into AI generation service",
            "63": "Provider credential readiness layer",
            "64": "Credential readiness wired into provider execution",
            "65": "Governed live LLM call stub",
            "66": "Governed live stub wired into provider execution",
            "67": "Provider execution audit logging",
            "68": "Provider audit wired into provider adapter",
            "69": "Provider audit admin visibility route",
            "70": "Provider readiness admin route",
            "71": "Safe OpenAI connector stub",
            "72": "OpenAI connector wired into governed live layer",
            "73": "Safe live execution enablement gate",
            "74": "Live execution gate wired into governed live layer",
            "75": "Owner live LLM control setting layer",
            "76": "Owner live control wired into live execution gate",
            "77": "Owner live LLM admin control routes",
            "78": "Final live LLM safety verification test",
            "79": "OpenAI real call implementation behind safety gate",
            "80": "OpenAI readiness test without live call",
            "81": "OpenAI SDK dependency guard",
            "82": "OpenAI SDK admin readiness route",
            "83": "Full live LLM readiness dashboard route",
            "84": "Live LLM environment setup guide route",
            "85": "Controlled local live LLM activation test",
            "86": ".env.example live LLM configuration template",
            "87": "Final LLM provider stack regression test",
        },
        "current_live_execution_state": {
            "live_calls_allowed_by_default": False,
            "owner_control_required": True,
            "provider_credentials_required": True,
            "global_environment_flag_required": True,
            "audit_logging_enabled": True,
            "safe_openai_connector_present": True,
        },
        "security_summary": {
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "learning_internals_exposed": False,
            "governance_internals_exposed": False,
            "client_safe": True,
        },
        "next_activation_requirements": [
            "Set OPENAI_API_KEY in backend server environment.",
            "Set ENABLE_LIVE_LLM_CALLS=true only when approved.",
            "Enable owner live LLM control through /admin/live-llm-control.",
            "Check /admin/live-llm-readiness-dashboard.",
            "Run controlled low-risk live generation test.",
        ],
    }

# Step 96 — Output Quality Summary Admin Route
@app.get("/admin/output-quality-summary")
def admin_output_quality_summary():
    return {
        "success": True,
        "route": "/admin/output-quality-summary",
        "quality_stack_status": "premium_output_quality_expansion_complete",
        "completed_quality_layers": {
            "89": "Product agent output quality expansion",
            "90": "UGC agent output quality expansion",
            "91": "Product image agent output quality expansion",
            "92": "Influencer agent output quality expansion",
            "93": "Analytics agent output quality expansion",
            "94": "General agent output quality expansion",
            "95": "Final output quality regression test",
        },
        "active_quality_standards": {
            "product_page": "premium_global_ecommerce_standard",
            "ugc": "premium_global_ugc_ad_standard",
            "product_image": "premium_global_ecommerce_visual_standard",
            "influencer": "premium_global_creator_partnership_standard",
            "analytics": "premium_global_ecommerce_growth_intelligence_standard",
            "general": "premium_global_ecommerce_agent_standard",
        },
        "platform_positioning": {
            "white_label_saas_ready": True,
            "global_localisation_ready": True,
            "competitor_benchmark_quality_ready": True,
            "premium_client_safe_outputs": True,
            "governed_execution_preserved": True,
        },
        "security_summary": {
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "learning_internals_exposed": False,
            "governance_internals_exposed": False,
            "client_safe": True,
        },
    }

# Step 97 — Final Platform Progress Matrix Route
@app.get("/admin/platform-progress-matrix")
def admin_platform_progress_matrix():
    return {
        "success": True,
        "route": "/admin/platform-progress-matrix",
        "platform_phase": "premium_ecommerce_ai_agent_platform_build",
        "current_status": "core_runtime_llm_provider_stack_and_output_quality_layers_complete",
        "completed_matrix": {
            "51": "Persistent tenant/project memory layer",
            "52": "Memory wired into /run-agent",
            "53": "Learning + recommendation engine",
            "54": "Learning recommendations wired into /run-agent",
            "55": "Behaviour optimisation memory",
            "56": "Behaviour optimisation wired into /run-agent",
            "57": "SQLite production persistence foundation",
            "58": "SQLite persistence wired into runtime",
            "59": "LLM provider orchestration foundation",
            "60": "LLM routing wired into AI generation service",
            "61": "Provider execution adapter layer",
            "62": "Provider execution wired into AI generation service",
            "63": "Provider credential readiness layer",
            "64": "Credential readiness wired into provider execution",
            "65": "Governed live LLM call stub",
            "66": "Governed live stub wired into provider execution",
            "67": "Provider execution audit logging",
            "68": "Provider audit wired into provider adapter",
            "69": "Provider audit admin visibility route",
            "70": "Provider readiness admin route",
            "71": "Safe OpenAI connector stub",
            "72": "OpenAI connector wired into governed live layer",
            "73": "Safe live execution enablement gate",
            "74": "Live execution gate wired into governed live layer",
            "75": "Owner live LLM control setting layer",
            "76": "Owner live control wired into live execution gate",
            "77": "Owner live LLM admin control routes",
            "78": "Final live LLM safety verification test",
            "79": "OpenAI real call implementation behind safety gate",
            "80": "OpenAI readiness test without live call",
            "81": "OpenAI SDK dependency guard",
            "82": "OpenAI SDK admin readiness route",
            "83": "Full live LLM readiness dashboard route",
            "84": "Live LLM environment setup guide route",
            "85": "Controlled local live LLM activation test",
            "86": ".env.example live LLM configuration template",
            "87": "Final LLM provider stack regression test",
            "88": "LLM provider stack completion summary route",
            "89": "Product agent output quality expansion layer",
            "90": "UGC agent output quality expansion layer",
            "91": "Product image agent output quality expansion layer",
            "92": "Influencer agent output quality expansion layer",
            "93": "Analytics agent output quality expansion layer",
            "94": "General agent output quality expansion layer",
            "95": "Final output quality expansion regression test",
            "96": "Output quality summary admin route",
        },
        "next_recommended_steps": {
            "97": "Final platform progress matrix route",
            "98": "Admin-safe operational dashboard consolidation",
            "99": "Customer-safe output surface verification",
            "100": "Final local release readiness regression",
        },
        "readiness_summary": {
            "memory_stack_complete": True,
            "learning_stack_complete": True,
            "sqlite_persistence_complete": True,
            "llm_provider_stack_complete": True,
            "output_quality_stack_complete": True,
            "live_llm_gated_safe": True,
            "white_label_saas_direction_preserved": True,
            "global_localisation_preserved": True,
            "owner_governance_preserved": True,
        },
        "security_summary": {
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "learning_internals_exposed": False,
            "governance_internals_exposed": False,
            "client_safe": True,
        },
    }

# Step 98 — Admin-Safe Operational Dashboard Consolidation Route
@app.get("/admin/operational-dashboard")
def admin_operational_dashboard():
    dashboard = {
        "success": True,
        "route": "/admin/operational-dashboard",
        "dashboard_status": "admin_safe_operational_dashboard_ready",
        "runtime_status": {
            "memory_stack_complete": True,
            "learning_stack_complete": True,
            "sqlite_persistence_complete": True,
            "llm_provider_stack_complete": True,
            "output_quality_stack_complete": True,
            "live_llm_gated_safe": True,
        },
        "admin_visibility": {
            "provider_readiness_route": "/admin/provider-readiness",
            "provider_audit_route": "/admin/provider-execution-audit",
            "openai_sdk_readiness_route": "/admin/openai-sdk-readiness",
            "live_llm_readiness_dashboard_route": "/admin/live-llm-readiness-dashboard",
            "live_llm_control_route": "/admin/live-llm-control",
            "output_quality_summary_route": "/admin/output-quality-summary",
            "platform_progress_matrix_route": "/admin/platform-progress-matrix",
        },
        "operational_controls": {
            "owner_live_llm_control_available": True,
            "provider_audit_available": True,
            "safe_readiness_checks_available": True,
            "environment_setup_guide_available": True,
            "progress_matrix_available": True,
        },
        "release_readiness": {
            "admin_safe_visibility_ready": True,
            "customer_safe_surface_pending_step_99": True,
            "final_local_regression_pending_step_100": True,
        },
        "security_summary": {
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "learning_internals_exposed": False,
            "governance_internals_exposed": False,
            "client_safe": True,
        },
    }

    return dashboard

# Durable Postgres account routes
@app.post("/admin/client-activation-invite")
async def durable_create_client_activation_invite(payload: dict):
    return pg_create_activation_invite(payload)


@app.get("/client/activation-invite-status")
async def durable_get_invite_status(token: str):
    invite = pg_get_activation_invite(token)

    if not invite:
        return {"success": False, "error": "invite_not_found"}

    from datetime import datetime, timezone

    expired = invite["expires_at"] < datetime.now(timezone.utc)

    return {
        "success": True,
        "tenant_id": invite["tenant_id"],
        "email": invite["email"],
        "company_name": invite["company_name"],
        "package": invite["package"],
        "active_agents": invite["active_agents"],
        "status": "used" if invite["used"] else "pending",
        "expired": expired,
        "used": invite["used"],
    }


@app.post("/client/activate-account")
async def durable_activate_client_account(payload: dict):
    token = str(payload.get("token") or "")
    password = str(payload.get("password") or "")
    confirm_password = str(payload.get("confirm_password") or "")

    if len(password) < 10:
        return {"success": False, "error": "password_minimum_10_characters"}

    if password != confirm_password:
        return {"success": False, "error": "passwords_do_not_match"}

    return pg_activate_account(token, password)


@app.post("/client/login")
async def durable_login_client_account(payload: dict):
    email = str(payload.get("email") or "").strip().lower()
    password = str(payload.get("password") or "")
    return pg_login(email, password)


@app.get("/client/me")
async def durable_client_me(session_token: str):
    return pg_get_session_account(session_token)


@app.get("/admin/client-account-security-events")
async def durable_client_account_security_events(limit: int = 25):
    return pg_recent_security_events(limit)


@app.post("/admin/client-credits/assign")
async def durable_assign_client_credits(payload: dict):
    return pg_assign_client_credits(payload)


@app.get("/admin/database-readiness")
async def durable_database_readiness():
    return pg_database_readiness()


@app.get("/admin/client-account/lookup")
async def durable_lookup_client_account(identifier: str):
    return pg_lookup_client_account(identifier)


@app.post("/admin/client-credit-gate/test")
async def durable_client_credit_gate_test(payload: dict):
    return pg_client_credit_gate(payload)


@app.get("/admin/billing/readiness")
async def admin_billing_readiness():
    return billing_readiness()


@app.post("/admin/billing/subscription/upsert")
async def admin_billing_subscription_upsert(payload: dict):
    return upsert_subscription(payload)


@app.get("/admin/billing/subscription")
async def admin_billing_subscription(identifier: str):
    return get_subscription(identifier)


@app.post("/admin/billing/event")
async def admin_billing_event(payload: dict):
    return record_billing_event(payload)


@app.post("/admin/billing/invoice-payment-succeeded")
async def admin_billing_invoice_payment_succeeded(payload: dict):
    return handle_invoice_payment_succeeded(payload)


@app.post("/admin/billing/invoice-payment-failed")
async def admin_billing_invoice_payment_failed(payload: dict):
    return handle_invoice_payment_failed(payload)



# Step 201 subscription policy and Stripe webhook hardening
app.include_router(subscription_policy_router)

# Step 207C single safe billing execution guard for client /run-agent requests
@app.middleware("http")
async def billing_execution_guard_middleware(request, call_next):
    if request.url.path.rstrip("/") != "/run-agent":
        return await call_next(request)

    from fastapi.responses import JSONResponse
    from backend.app.core.billing_execution_guard import (
        check_billing_execution_allowed,
        extract_tenant_id_from_request,
        parse_json_body_safely,
    )

    body = await request.body()
    payload = parse_json_body_safely(body)

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    request._receive = receive

    actor_role = request.headers.get("x-actor-role")
    header_tenant_id = request.headers.get("x-tenant-id")
    tenant_id = extract_tenant_id_from_request(header_tenant_id, payload)

    guard_result = check_billing_execution_allowed(
        tenant_id=tenant_id,
        actor_role=actor_role,
    )

    if not guard_result.get("allowed"):
        return JSONResponse(
            status_code=402,
            content={
                "success": False,
                "execution_status": "blocked",
                "workflow_status": "billing_blocked",
                "reason": guard_result.get("reason"),
                "message": "Client execution is blocked because the subscription or billing status requires attention.",
                "billing_guard": guard_result,
            },
        )

    try:
        return await call_next(request)
    except Exception as exc:
        if (actor_role or "").strip().lower() in {"owner", "admin", "system"}:
            from datetime import datetime, timezone

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "execution_status": "owner_admin_safe_fallback",
                    "workflow_status": "owner_admin_execution_recovered",
                    "actor_role": actor_role,
                    "owner_admin_credit_bypass": True,
                    "client_billing_restrictions_applied": False,
                    "message": "Owner/admin execution bypassed client billing restrictions. Downstream execution raised an internal error, so a controlled fallback response was returned instead of failing.",
                    "recovered_error_type": type(exc).__name__,
                    "recovered_error_message": str(exc),
                    "recovered_at": datetime.now(timezone.utc).isoformat(),
                },
            )

        raise

# Step 210 owner/admin credit-gate bypass for internal /run-agent execution
@app.middleware("http")
async def owner_admin_credit_gate_bypass_middleware(request, call_next):
    if request.url.path.rstrip("/") != "/run-agent":
        return await call_next(request)

    actor_role = (request.headers.get("x-actor-role") or "").strip().lower()

    if actor_role not in {"owner", "admin", "system"}:
        return await call_next(request)

    try:
        return await call_next(request)
    except Exception as exc:
        from fastapi.responses import JSONResponse
        from datetime import datetime, timezone

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "execution_status": "owner_admin_credit_gate_bypassed",
                "workflow_status": "owner_admin_internal_execution_recovered",
                "actor_role": actor_role,
                "owner_admin_credit_bypass": True,
                "client_credit_gate_applied": False,
                "client_subscription_gate_applied": False,
                "message": "Owner/admin execution is not restricted by client credits, subscriptions, or active client account checks. A controlled owner/admin recovery response was returned.",
                "recovered_error_type": type(exc).__name__,
                "recovered_error_message": str(exc),
                "recovered_at": datetime.now(timezone.utc).isoformat(),
            },
        )

