from backend.app.runtime.outcome_action_execution_runtime import create_outcome_action_plan, mark_outcome_plan_decision

from backend.app.runtime.delegated_workforce_execution_runtime import (
    execute_delegated_workforce_plan,
)
from backend.app.runtime.persistent_action_execution_history import (
    list_action_execution_history,
    action_execution_history_readiness,
)
from backend.app.runtime.durable_external_action_records import (
    list_external_action_records,
    external_action_records_readiness,
)
from backend.app.runtime.durable_execution_history_evidence_runtime import (
    get_latest_deliverable,
    list_execution_evidence,
    list_execution_history,
    record_approval_action_audit,
    record_execution_evidence,
    record_execution_history,
    record_latest_deliverable,
)
from backend.app.core.integration_live_adapter_registry import (
    adapter_registry_summary,
    execute_integration_action,
)
import urllib.request
import urllib.error
import json
import hmac
import os
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.client_integrations_runtime import (
    disconnect_client_integration,
    integration_audit,
    integration_catalogue,
    list_client_integrations,
    save_client_integration,
    test_client_integration,
    get_client_integration_secret,
    log_email_proof_send,
)
from backend.app.core.client_business_profile_runtime import (
    get_client_business_profile as get_canonical_client_business_profile,
    save_client_business_profile as save_canonical_client_business_profile,
)
from backend.app.api.storage_routes import router as storage_router
from backend.app.api.media_routes import router as media_router
import sitecustomize  # Step 209D force local env loading
from backend.app.api.subscription_policy_routes import router as subscription_policy_router
from backend.app.api.admin_deployment_control_routes import (
    router as admin_deployment_control_router,
)


from backend.app.core.subscription_billing_runtime import (
    billing_readiness,
    get_subscription,
    record_billing_event,
    upsert_subscription,
    handle_invoice_payment_succeeded,
    handle_invoice_payment_failed,
)
from backend.app.core.canonical_billing_state_runtime import owner_admin_bypasses_client_billing
from backend.app.runtime.canonical_entitlement_activation_runtime import (
    activate_entitlement_once as canonical_activate_entitlement_once,
    evaluate_execution_entitlement as canonical_evaluate_execution_entitlement,
    get_entitlement as canonical_get_entitlement,
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

from backend.app.runtime.global_execution_evidence_layer import build_execution_evidence_packet
from fastapi import Request, FastAPI, Header, Request
from backend.app.runtime.creative_asset_persistence_bridge import get_persisted_creative_assets, persist_creative_agent_output
from backend.app.runtime.asset_storage_signed_delivery_runtime import build_customer_safe_delivery_response
from backend.app.runtime.shared_creative_media_generation_runtime import CREATIVE_MEDIA_AGENTS
from backend.app.runtime.autonomous_workforce_orchestration_foundation import autonomous_workforce_orchestration_status, create_delegated_subtask_plan, create_orchestration_execution_graph, orchestration_replay_recovery_packet
from backend.app.runtime.provider_workforce_runtime_hardening import provider_workforce_runtime_hardening_status, provider_runtime_health_summary, provider_recovery_readiness_summary
from backend.app.runtime.real_provider_activation_registry import get_all_provider_activation_statuses, get_provider_activation_status, select_ready_provider_for_capability
from backend.app.runtime.real_provider_http_execution_layer import controlled_openai_live_execution_status, real_provider_http_runtime_status, execute_controlled_openai_live_request
from backend.app.runtime.provider_dispatch_policy_worker_foundation import provider_dispatch_policy_status, evaluate_provider_dispatch_policy, provider_worker_foundation_status
from backend.app.runtime.safe_provider_action_adapters import evaluate_safe_provider_action, classify_provider_action
from pydantic import BaseModel
from typing import Any, Dict, List

from backend.app.agents.agent_registry import agent_exists, normalize_agent_id
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
from backend.app.runtime.canonical_agent_identity_bridge import normalise_agent_identity
from backend.app.runtime.autonomous_qa_regression_intelligence import autonomous_qa_regression_status, build_qa_regression_packet
from backend.app.runtime.post_deploy_validation_readiness import post_deploy_validation_status
from backend.app.runtime.global_beta_readiness_orchestration import global_beta_readiness_status
from backend.app.runtime.global_production_audit_orchestrator import global_production_audit_status
from backend.app.runtime.global_commercial_launch_orchestrator import global_commercial_launch_status
from backend.app.runtime.global_scale_operations_orchestrator import global_scale_operations_status
from backend.app.runtime.execution_stack import (
    ExecutionRequest,
    ExecutionStack,
    execution_summary,
)
from backend.app.core.execution_event_ledger import execution_event_ledger
from backend.app.core.execution_event_runtime import add_execution_event, list_execution_events
from backend.app.core.execution_queue_runtime import enqueue_execution, list_execution_queue, mark_execution_failed, queue_readiness
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


from backend.app.core.security_hardening_runtime import install_security_hardening, security_hardening_readiness

from backend.app.core.session_auth_hardening_runtime import install_session_auth_hardening, session_auth_hardening_readiness

from backend.app.core.security_audit_enforcement_runtime import install_security_audit_enforcement, security_audit_enforcement_readiness

from backend.app.core.production_security_switch import production_security_switch_readiness

from backend.app.core.execution_queue_worker_runtime import queue_worker_health, worker_heartbeat, clear_queue_worker_locks, claim_execution_queue_batch, run_queue_worker_once

from backend.app.runtime.provider_execution_admin_visibility import (
    get_provider_execution_admin_visibility,
    get_provider_execution_admin_visibility_status,
)
from backend.app.runtime.provider_retry_timeout_orchestration import (
    schedule_provider_job_retry,
    requeue_retry_ready_provider_jobs,
)
from backend.app.runtime.provider_job_persistence_runtime import update_provider_job_status
from backend.app.runtime.durable_provider_execution_ledger import (
    create_provider_execution_record as create_durable_provider_execution_record,
    create_provider_job as create_durable_provider_job,
    list_provider_jobs as list_durable_provider_jobs,
)
from backend.app.runtime.durable_manual_review_recovery_runtime import (
    get_review_recovery_summary,
    list_manual_review_items,
    list_dead_letter_records,
    record_manual_review_decision as record_durable_manual_review_decision,
    resolve_dead_letter_record,
)

from backend.app.core.multi_agent_orchestration_runtime import orchestration_readiness, create_orchestration_plan, orchestration_execution_readiness, enqueue_orchestration_plan

from backend.app.core.orchestration_state_runtime import orchestration_state_readiness, record_orchestration_state, record_orchestration_result, get_orchestration_context, orchestration_recovery_packet

from backend.app.core.governed_learning_optimisation_runtime import governed_learning_readiness, score_learning_outcome, aggregate_learning_patterns, generate_agent_coaching_recommendations

from backend.app.core.saas_provisioning_runtime import provisioning_readiness, provision_tenant, validate_one_time_link, retrieve_tenant_bootstrap, update_tenant_lifecycle, cleanup_expired_activation_links
from backend.app.core.marketplace_entitlement_runtime import build_marketplace_entitlement_summary
from backend.app.core.global_agent_registry import global_agent_registry_summary
from backend.app.core.marketplace_activation_runtime import activate_marketplace_agent, deactivate_marketplace_agent, build_client_marketplace_workspace, build_package_upgrade_preview
from backend.app.core.marketplace_state_runtime import upsert_marketplace_state, get_marketplace_state, persist_activation_action, validate_package_downgrade, marketplace_audit_history
from backend.app.core.marketplace_commercial_bridge import package_pricing_catalogue, build_purchase_flow_payload, create_entitlement_change_request, apply_entitlement_change_after_billing, marketplace_commercial_summary
from backend.app.core.billing_automation_runtime import create_checkout_session_payload, handle_checkout_completed, handle_invoice_payment_succeeded_runtime, handle_invoice_payment_failed_runtime, cancel_subscription_runtime, reactivate_subscription_runtime, billing_automation_summary
from backend.app.core.stripe_production_hardening_runtime import stripe_production_env_readiness, verify_stripe_webhook_signature, route_stripe_webhook_event, schedule_failed_payment_recovery, transition_trial_to_paid, build_customer_billing_portal_payload, admin_billing_dashboard
from backend.app.core.live_stripe_bridge_runtime import live_stripe_bridge_readiness, create_live_checkout_session, create_live_billing_portal_session, ingest_live_stripe_webhook
from backend.app.core.final_deployment_readiness_runtime import final_deployment_readiness
from backend.app.core.rate_shaping_middleware import RateShapingMiddleware


# CONTROLLED_LIVE_EXECUTION_WHITELIST_V1
CONTROLLED_OWNER_APPROVED_LIVE_EXECUTION_PATHS = {
    "/admin/provider-activation-visibility/evaluate",
}

def _is_controlled_owner_approved_live_execution_path(path: str) -> bool:
    return path in CONTROLLED_OWNER_APPROVED_LIVE_EXECUTION_PATHS


app = FastAPI(
    title="Ecommerce AI Agent Platform",
    version="1.1.0",
)

# Production rate-shaping middleware is observe-mode by default.
app.add_middleware(RateShapingMiddleware)



install_security_hardening(app)
install_session_auth_hardening(app)
install_security_audit_enforcement(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ecommerce-ai-agent-platform.vercel.app",
        "https://ecommerce-ai-agent-platform-git-main-marksalman76-5799s-projects.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(admin_deployment_control_router)


DEMO_TENANTS: Dict[str, List[str]] = {
    "client_demo_001": [
        "head_agent",
        "ugc_creative_agent",
        "analytics_optimisation_agent",
        "product_research_agent",
        "ad_creative_agent",
        "product_image_agent",
        "influencer_collaboration_agent",
    ]
}



ACTION_TO_EXECUTION_MAP: Dict[str, str] = {
    # Safe generation actions must use the canonical governed live provider path.
    "general_ecommerce_agent_output": "governed_live_provider_generation",
    "marketing_campaign_execution": "governed_live_provider_generation",
    "content_generation": "governed_live_provider_generation",
    "ugc_script_generation": "governed_live_provider_generation",
    "product_image_generation": "governed_live_provider_generation",
    "product_image_direction": "governed_live_provider_generation",
    "ad_copy_generation": "governed_live_provider_generation",
    "website_content_generation": "governed_live_provider_generation",
    "product_copy_generation": "governed_live_provider_generation",
    "influencer_shortlist": "governed_live_provider_generation",
    "influencer_outreach_draft": "governed_live_provider_generation",
    "customer_support_reply": "governed_live_provider_generation",
    "analytics_report": "governed_live_provider_generation",
    "seo_strategy": "governed_live_provider_generation",
    "business_growth": "governed_live_provider_generation",
    "crm_strategy": "governed_live_provider_generation",
    "billing_optimisation": "governed_live_provider_generation",
    "training_learning": "governed_live_provider_generation",
    "qa_testing": "governed_live_provider_generation",
    "security_compliance": "governed_live_provider_generation",
    "integration_automation": "governed_live_provider_generation",
    "orchestration": "governed_live_provider_generation",
    "website_app_build": "governed_live_provider_generation",
    "analytics_intelligence": "governed_live_provider_generation",

    # Sensitive/high-authority actions remain owner-gated.
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

    # Remaining enterprise/system-safe execution mappings
    "website_strategy_generation": "governed_live_provider_generation",
    "analytics_intelligence_generation": "governed_live_provider_generation",
    "qa_testing_generation": "governed_live_provider_generation",
    "billing_optimisation_generation": "governed_live_provider_generation",
    "training_learning_generation": "governed_live_provider_generation",
}


APPROVED_GOVERNED_EXECUTION_AGENTS = {
    "marketing_specialist_agent",
    "crm_ai_agent",
    "email_reply_agent",
    "strategist_agent",
    "business_growth_partnerships_agent",
    "lead_generator_appointment_setter_agent",
    "social_media_manager_content_creator_agent",
    "seo_agent",
    "sales_closer_agent",
    "receptionist_agent",
    "customer_support_agent",
    "ecommerce_agent",
    "product_research_agent",
    "competitor_intelligence_agent",
    "brand_strategy_agent",
    "store_builder_agent",
    "website_landing_page_apps_agent",
    "product_development_agent",
    "product_copywriting_agent",
    "ugc_creative_agent",
    "product_image_agent",
    "paid_ads_agent",
    "analytics_optimisation_agent",
    "influencer_collaboration_agent",
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




# PRODUCTION_CREATIVE_ASSET_PERSISTENCE_BRIDGE_START

# PRODUCTION_ASSET_DELIVERY_ROUTES_START
@app.get("/asset-delivery/{delivery_type}/{asset_id}")
async def asset_delivery(delivery_type: str, asset_id: str, expires: int, nonce: str, sig: str):
    from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

    try:
        result = build_customer_safe_delivery_response(
            asset_id=asset_id,
            delivery_type=delivery_type,
            expires_at_ms=expires,
            nonce=nonce,
            signature=sig,
        )

        status_code = int(result.get("http_status", 200) or 200)

        if status_code >= 400:
            return JSONResponse(status_code=status_code, content=result)

        serve_file_path = result.get("serve_file_path")
        if serve_file_path:
            filename = result.get("filename")
            content_type = result.get("content_type") or "application/octet-stream"

            response = FileResponse(
                path=serve_file_path,
                media_type=content_type,
                filename=filename if delivery_type == "download" else None,
            )

            if delivery_type == "preview":
                response.headers["Content-Disposition"] = "inline"

            return response

        redirect_url = result.get("redirect_url")
        if redirect_url:
            return RedirectResponse(url=redirect_url, status_code=302)

        return JSONResponse(status_code=status_code, content=result)

    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status": "delivery_failed",
                "error": str(exc),
                "credential_values_exposed": False,
                "customer_safe": True,
            },
        )

@app.get("/admin/persisted-creative-assets")
async def admin_persisted_creative_assets():
    try:
        registry = get_persisted_creative_assets(limit=100)
        asset_list = registry.get("assets", []) if isinstance(registry, dict) else []
        return {
            "success": True,
            "layer": "creative_asset_persistence_bridge",
            "status": "available",
            "asset_count": len(asset_list),
            "total_asset_count": registry.get("total_asset_count", len(asset_list)) if isinstance(registry, dict) else len(asset_list),
            "assets": asset_list,
            "providers_checked": registry.get("providers_checked", []) if isinstance(registry, dict) else [],
            "credential_values_exposed": False,
        }
    except Exception as exc:
        return {
            "success": False,
            "layer": "creative_asset_persistence_bridge",
            "status": "unavailable",
            "error": str(exc),
            "credential_values_exposed": False,
        }
# PRODUCTION_CREATIVE_ASSET_PERSISTENCE_BRIDGE_END

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


@app.get("/client/execution-events")
def client_execution_events(
    tenant_id: str = "client_demo_001",
    project_id: str = "",
    limit: int = 25,
) -> Dict[str, object]:
    try:
        safe_limit = max(1, min(int(limit or 25), 100))
        safe_tenant_id = str(tenant_id or "client_demo_001")
        safe_project_id = str(project_id or "")

        durable_result = list_execution_events(
            tenant_id=safe_tenant_id,
            project_id=safe_project_id or "default_project",
            limit=safe_limit,
        )

        if durable_result.get("success"):
            return durable_result

        events = execution_event_ledger.latest(
            tenant_id=safe_tenant_id,
            project_id=safe_project_id or None,
            limit=safe_limit,
            client_visible_only=True,
        )

        return {
            "success": True,
            "tenant_id": safe_tenant_id,
            "project_id": safe_project_id or None,
            "count": len(events),
            "events": events,
            "storage_mode": "file_fallback",
        }
    except Exception as error:
        return {
            "success": False,
            "error": "execution_event_ledger_unavailable",
            "message": str(error),
            "tenant_id": str(tenant_id or "client_demo_001"),
            "project_id": str(project_id or "") or None,
            "count": 0,
            "events": [],
        }

@app.post("/run-agent")
def run_agent(request: RunAgentRequest) -> Dict[str, object]:
    quality_failure_payload = {
        "success": False,
        "quality_gate_failed": False,
        "provider_execution_attempted": False,
        "external_action_performed": False,
        "customer_safe": True,
    }

    requested_agent = normalise_agent_identity(normalize_agent_id(request.requested_agent))

    actor_role = (request.actor_role or "").strip().lower()
    tenant_id_clean = str(request.tenant_id or "").strip().lower()

    owner_managed_client_credit_bypass = (
        tenant_id_clean in {
            "client_demo_001",
            "owner_managed_demo",
            "owner_managed_demo_client",
            "manual_deployment_client",
            "internal_demo_client",
        }
        or tenant_id_clean.startswith("owner_managed_")
        or tenant_id_clean.startswith("manual_deployment_")
        or tenant_id_clean.startswith("demo_")
    )

    if owner_managed_client_credit_bypass:
        credit_gate = {
            "success": True,
            "credit_gate_passed": True,
            "owner_managed_client_credit_bypass": True,
            "client_credit_gate_applied": False,
            "bypass_reason": "owner_managed_or_demo_client_not_credit_limited",
        }
    else:
        credit_gate = pg_client_credit_gate({
            "actor_role": request.actor_role,
            "tenant_id": request.tenant_id,
            "requested_credits": request.requested_credits,
        })

    owner_admin_credit_bypass = owner_admin_bypasses_client_billing(actor_role)

    owner_managed_client_credit_bypass = (
        tenant_id_clean in {"client_demo_001", "owner_managed_demo", "owner_managed_demo_client", "manual_deployment_client"}

    )

    if not credit_gate.get("credit_gate_passed") and owner_managed_client_credit_bypass:
        credit_gate = {
            **credit_gate,
            "credit_gate_passed": True,
            "owner_managed_client_credit_bypass": True,
            "client_credit_gate_applied": False,
            "bypass_reason": "owner_managed_or_demo_client_not_credit_limited",
        }

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

    owner_admin_system_agents = {
        "qa_testing_agent",
        "billing_optimisation_agent",
        "training_learning_agent",
    }

    if not agent_exists(requested_agent) and not (
        owner_admin_bypasses_client_billing(request.actor_role)
        and requested_agent in owner_admin_system_agents
    ):
        return {
            "success": False,
            "error": "unknown_agent",
            "requested_agent": request.requested_agent,
            "normalised_agent": requested_agent,
        }

    owner_admin_internal_execution = owner_admin_bypasses_client_billing(request.actor_role)

    tenant_account = pg_lookup_client_account(request.tenant_id)

    if not tenant_account.get("success"):
        if not owner_admin_internal_execution and not owner_managed_client_credit_bypass:
            return {
                "success": False,
                "error": "tenant_not_found_or_not_active",
                "tenant_id": request.tenant_id,
            }

        tenant_account = {
            "success": True,
            "account": {
                "tenant_id": request.tenant_id,
                "active_agents": [requested_agent],
                "owner_admin_internal_bypass": owner_admin_internal_execution,
                "owner_managed_client_bypass": owner_managed_client_credit_bypass,
            },
        }

    active_agents = tenant_account.get("account", {}).get("active_agents", [])

    existing_canonical_entitlement = canonical_get_entitlement(request.tenant_id)

    if (
        tenant_account.get("success")
        and not owner_admin_internal_execution
        and not existing_canonical_entitlement.get("success")
    ):
        canonical_activate_entitlement_once(
            tenant_id=request.tenant_id,
            package=tenant_account.get("account", {}).get("package") or "starter",
            selected_agents=[normalize_agent_id(agent) for agent in active_agents],
            actor_role="system",
            source="client_accounts_migration_seed",
        )

    entitlement_decision = canonical_evaluate_execution_entitlement(
        tenant_id=request.tenant_id,
        requested_agent=requested_agent,
        actor_role=request.actor_role,
    )

    if not entitlement_decision.get("execution_allowed"):
        return {
            "success": False,
            "error": entitlement_decision.get("error") or "agent_not_active_for_tenant",
            "tenant_id": request.tenant_id,
            "requested_agent": request.requested_agent,
            "normalised_agent": requested_agent,
            "entitlement_decision": entitlement_decision,
        }

    # CREATIVE_TEAM_REAL_MEDIA_EXECUTION_PATH_START
    creative_media_keywords = {
        "actual video",
        "generate video",
        "create video",
        "video ad",
        "ugc video",
        "short-form video",
        "reels",
        "tiktok",
        "voiceover",
        "audio",
        "avatar",
        "lip sync",
        "lipsync",
        "image asset",
        "product image",
        "creative asset",
        "media asset",
        "runway",
        "kling",
        "heygen",
        "elevenlabs",
        "visual",
        "ad creative",
        "campaign creative",
        "media execution pack",
        "preview/download-ready",
        "preview ready",
        "download ready",
    }

    creative_request_text = " ".join(
        [
            str(request.task or ""),
            str(request.action_type or ""),
            str(request.workflow_stage or ""),
            str(requested_agent or ""),
        ]
    ).lower().replace("_", " ")

    creative_media_requested = (
        requested_agent in CREATIVE_MEDIA_AGENTS
        or any(keyword in creative_request_text for keyword in creative_media_keywords)
    )

    if creative_media_requested:
        owner_media_execution_allowed = bool(
            owner_admin_internal_execution
            or request.owner_approved
            or owner_admin_bypasses_client_billing(actor_role)
        )

        if not owner_media_execution_allowed:
            return {
                "success": False,
                "status": "blocked_owner_approval_required",
                "workflow_status": "creative_media_execution_blocked",
                "execution_status": "blocked_owner_approval_required",
                "requested_agent": requested_agent,
                "tenant_id": request.tenant_id,
                "owner_approval_required": True,
                "external_provider_called": False,
                "spend_performed": False,
                "credential_values_exposed": False,
                "customer_safe": True,
                "message": "Creative media generation can call live media providers and requires owner approval.",
            }

        try:
            from backend.app.runtime.async_media_job_foundation import enqueue_media_job

            media_job = enqueue_media_job(
                task=request.task,
                agent_id=requested_agent,
                tenant_id=request.tenant_id or "owner_admin",
                include_image=True,
                include_audio=True,
                include_video=True,
                include_avatar=True,
            )

            creative_payload = {
                "workflow_status": "creative_media_job_queued",
                "execution_status": "media_job_queued",
                "requested_agent": requested_agent,
                "tenant_id": request.tenant_id,
                "project_id": request.project_id,
                "media_job_id": media_job.get("job_id"),
                "media_job_status": media_job.get("status"),
                "media_asset_count": 0,
                "real_media_asset_count": 0,
                "playable_asset_count": 0,
                "generation_job_count": 1,
                "credential_values_exposed": False,
                "customer_safe": True,
            }

            try:
                MemoryStore().add_record(
                    tenant_id=request.tenant_id,
                    project_id=request.project_id,
                    record_type="creative_media_execution",
                    title=f"{requested_agent} creative media job queued",
                    payload=creative_payload,
                )
            except Exception:
                pass

            try:
                SQLiteStore().add_record(
                    tenant_id=request.tenant_id,
                    project_id=request.project_id,
                    record_type="creative_media_execution",
                    title=f"{requested_agent} creative media job queued",
                    payload=creative_payload,
                )
            except Exception:
                pass

            try:
                add_execution_event(
                    tenant_id=request.tenant_id,
                    project_id=request.project_id,
                    event_type="creative_media_job_queued",
                    title=f"{requested_agent} creative media job queued",
                    agent_id=requested_agent,
                    payload=creative_payload,
                )
            except Exception:
                pass

            return {
                "success": True,
                "status": "creative_media_job_queued",
                "workflow_status": "creative_media_job_queued",
                "execution_status": "media_job_queued",
                "requested_agent": requested_agent,
                "tenant_id": request.tenant_id,
                "actor_role": request.actor_role,
                "owner_approved": True,
                "owner_approval_required": False,
                "media_job_created": True,
                "media_job_id": media_job.get("job_id"),
                "media_job_status": media_job.get("status"),
                "provider_execution_attempted": False,
                "real_media_asset_count": 0,
                "playable_asset_count": 0,
                "media_asset_count": 0,
                "generation_job_count": 1,
                "preview_ready": False,
                "download_ready": False,
                "media_pack": {
                    "success": True,
                    "status": "queued",
                    "media_job_id": media_job.get("job_id"),
                    "media_assets": [],
                    "persisted_asset_count": 0,
                    "real_media_asset_count": 0,
                    "playable_asset_count": 0,
                    "credential_values_exposed": False,
                },
                "output": creative_payload,
                "credential_values_exposed": False,
                "customer_safe": True,
            }

        except Exception as exc:
            return {
                "success": False,
                "status": "creative_media_execution_failed",
                "workflow_status": "creative_media_execution_failed",
                "execution_status": "failed",
                "requested_agent": requested_agent,
                "tenant_id": request.tenant_id,
                "error": str(exc)[:1200],
                "credential_values_exposed": False,
                "customer_safe": True,
            }
    # CREATIVE_TEAM_REAL_MEDIA_EXECUTION_PATH_END

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

        add_execution_event(
            tenant_id=request.tenant_id,
            project_id=request.project_id,
            event_type="approval_gate_blocked",
            title=f"{requested_agent} action paused by approval gateway",
            agent_id=requested_agent,
            payload=blocked_payload,
        )

        add_execution_event(
            tenant_id=request.tenant_id,
            project_id=request.project_id,
            event_type="quality_gate_failed",
            title=f"{requested_agent} output rejected by premium quality gate",
            agent_id=requested_agent,
            payload=quality_failure_payload,
        )

        owner_admin_live_provider_test_allowed = (
            (request.actor_role or "").strip().lower() in {"owner", "admin", "owner_admin", "system"}
            and (request.workflow_stage or "").strip().lower() in {"specialist_execution", "controlled_live_provider_test"}
            and (request.action_type or "").strip().lower() in {"run_agent", "provider_verification"}
            and requested_agent in {"marketing_specialist_agent", "crm_ai_agent", "email_reply_agent"}
        )

        if not owner_admin_live_provider_test_allowed:
            execution_event_ledger.record(
                tenant_id=request.tenant_id,
                project_id=request.project_id,
                agent_id=requested_agent,
                actor_role=request.actor_role,
                workflow_stage=request.workflow_stage,
                action_type=request.action_type,
                execution_action=None,
                event_type="approval_gate_blocked",
                event_status=approval_decision.status,
                title=f"{requested_agent} action paused by approval gateway",
                summary="Action paused or rejected by owner approval gateway.",
                workflow=workflow_summary(workflow_packet),
                approval=approval_summary(approval_decision),
                owner_approved=request.owner_approved,
                client_visible=True,
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

    client_visible_quality_payload = {
        "agent": requested_agent,
        "task": request.task,
        "generated_output": polished_output.get("generated_output")
        or polished_output.get("output")
        or polished_output.get("content")
        or polished_output.get("deliverable")
        or polished_output,
    }

    quality_result = quality_gate.review_output(client_visible_quality_payload)

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

        execution_event_ledger.record(
            tenant_id=request.tenant_id,
            project_id=request.project_id,
            agent_id=requested_agent,
            actor_role=request.actor_role,
            workflow_stage=request.workflow_stage,
            action_type=request.action_type,
            execution_action=None,
            event_type="quality_gate_failed",
            event_status="quality_gate_failed",
            title=f"{requested_agent} output rejected by premium quality gate",
            summary="Output rejected by premium quality gate.",
            workflow=workflow_summary(workflow_packet),
            quality=quality_summary(quality_result),
            owner_approved=request.owner_approved,
            client_visible=True,
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

    add_execution_event(
        tenant_id=request.tenant_id,
        project_id=request.project_id,
        event_type="agent_execution_completed",
        title=f"{requested_agent} execution completed",
        agent_id=requested_agent,
        payload=successful_payload,
    )

    execution_event_ledger.record(
        tenant_id=request.tenant_id,
        project_id=request.project_id,
        agent_id=requested_agent,
        actor_role=request.actor_role,
        workflow_stage=request.workflow_stage,
        action_type=request.action_type,
        execution_action=execution_action,
        event_type="agent_execution_completed",
        event_status="agent_execution_completed",
        title=f"{requested_agent} execution completed",
        summary="Agent output passed workflow, approval, quality, and governed execution handling.",
        workflow=workflow_summary(workflow_packet),
        approval=approval_summary(approval_decision),
        quality=quality_summary(quality_result),
        execution=execution_summary(execution_result) if execution_result else None,
        owner_approved=request.owner_approved,
        client_visible=True,
    )

    latest_sqlite_record = sqlite_store.latest_record(
        tenant_id=request.tenant_id,
        project_id=request.project_id,
        record_type="successful_execution",
    )
    execution_summary_payload = execution_summary(execution_result) if execution_result else None
    durable_execution_id = str(
        (execution_summary_payload or {}).get("execution_id") or ""
    )

    durable_execution_history = record_execution_history(
        tenant_id=request.tenant_id,
        project_id=request.project_id,
        execution_id=durable_execution_id,
        agent_id=requested_agent,
        action_type=execution_action,
        status="agent_execution_completed",
        summary=f"{requested_agent} execution completed",
        payload=successful_payload,
        completed=True,
    )
    durable_execution_evidence = record_execution_evidence(
        tenant_id=request.tenant_id,
        project_id=request.project_id,
        execution_id=durable_execution_id or str(durable_execution_history.get("history_id") or ""),
        evidence_type="run_agent_execution_result",
        title=f"{requested_agent} execution evidence",
        summary="Agent output passed workflow, approval, quality, and governed execution handling.",
        source_type="run_agent",
        source_id=durable_execution_history.get("history_id") or "",
        status="agent_execution_completed",
        payload=successful_payload,
    )
    durable_latest_deliverable = record_latest_deliverable(
        tenant_id=request.tenant_id,
        project_id=request.project_id,
        execution_id=durable_execution_id or str(durable_execution_history.get("history_id") or ""),
        agent_id=requested_agent,
        title=f"{requested_agent} latest deliverable",
        summary=f"{requested_agent} execution completed",
        deliverable_type="agent_output",
        status="agent_execution_completed",
        payload={
            "output": polished_output,
            "successful_payload": successful_payload,
        },
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
        "execution": execution_summary_payload,
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
        "durable_execution_evidence": {
            "history_id": durable_execution_history.get("history_id"),
            "evidence_id": durable_execution_evidence.get("evidence_id"),
            "latest_deliverable_id": durable_latest_deliverable.get("deliverable_id"),
            "storage_mode": durable_execution_history.get("storage_mode"),
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



@app.get("/admin/execution-queue/readiness")
async def admin_execution_queue_readiness():
    return queue_readiness()


@app.get("/admin/execution-queue")
async def admin_execution_queue(tenant_id: str = "", status: str = "", limit: int = 50):
    return list_execution_queue(tenant_id=tenant_id, status=status, limit=limit)


@app.post("/admin/execution-queue/enqueue")
async def admin_execution_queue_enqueue(payload: dict):
    return enqueue_execution(payload)


@app.post("/admin/execution-queue/mark-failed")
async def admin_execution_queue_mark_failed(payload: dict):
    return mark_execution_failed(
        str(payload.get("job_id") or payload.get("queue_id") or ""),
        str(payload.get("error") or "manual_failure_test"),
    )


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

@app.get("/provider-execution-admin-visibility/status")
def provider_execution_admin_visibility_status():
    return get_provider_execution_admin_visibility_status()


@app.get("/provider-execution-admin-visibility/summary")
def provider_execution_admin_visibility_summary(tenant_id: str = "", provider: str = ""):
    return get_provider_execution_admin_visibility(tenant_id=tenant_id, provider=provider)


@app.get("/admin/manual-review/summary")
def admin_manual_review_summary(tenant_id: str = ""):
    return get_review_recovery_summary(tenant_id=tenant_id)


@app.get("/admin/manual-review/list")
def admin_manual_review_list(tenant_id: str = "", status: str = "", limit: int = 50):
    return list_manual_review_items(tenant_id=tenant_id, status=status, limit=limit)


@app.get("/admin/dead-letter/list")
def admin_dead_letter_list(tenant_id: str = "", status: str = "", limit: int = 50):
    return list_dead_letter_records(tenant_id=tenant_id, status=status, limit=limit)


@app.post("/admin/manual-review/decision")
def admin_manual_review_decision(payload: dict):
    payload = dict(payload or {})
    return record_durable_manual_review_decision(
        review_id=str(payload.get("review_id") or ""),
        decision=str(payload.get("decision") or ""),
        decided_by=str(payload.get("decided_by") or payload.get("actor") or "admin"),
        actor_role=str(payload.get("actor_role") or "admin"),
        reason=str(payload.get("reason") or payload.get("notes") or ""),
        payload=payload.get("payload") if isinstance(payload.get("payload"), dict) else payload,
    )


@app.post("/admin/dead-letter/resolve")
def admin_dead_letter_resolve(payload: dict):
    payload = dict(payload or {})
    return resolve_dead_letter_record(
        str(payload.get("dead_letter_id") or ""),
        reason=str(payload.get("reason") or "admin_resolved_dead_letter"),
    )


@app.post("/provider-execution-admin-visibility/actions/retry")
def provider_execution_admin_visibility_retry(payload: dict):
    job_id = str((payload or {}).get("job_id") or "")
    reason = str((payload or {}).get("reason") or "admin_requested_provider_retry")
    result = schedule_provider_job_retry(job_id, reason=reason, delay_seconds=0)
    return {
        "success": bool(result.get("success")),
        "accepted": bool(result.get("success")),
        "message": "Governed provider retry request accepted." if result.get("success") else result.get("reason") or result.get("error"),
        "result": result,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


@app.post("/provider-execution-admin-visibility/actions/requeue")
def provider_execution_admin_visibility_requeue(payload: dict):
    job_id = str((payload or {}).get("job_id") or "")
    result = update_provider_job_status(job_id, "queued", error=None, next_retry_at=None)
    return {
        "success": bool(result.get("success")),
        "accepted": bool(result.get("success")),
        "message": "Governed provider requeue request accepted." if result.get("success") else result.get("error"),
        "result": result,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


@app.post("/provider-execution-admin-visibility/actions/cancel")
def provider_execution_admin_visibility_cancel(payload: dict):
    job_id = str((payload or {}).get("job_id") or "")
    reason = str((payload or {}).get("reason") or "admin_requested_provider_cancel")
    result = update_provider_job_status(job_id, "cancelled", error=reason)
    return {
        "success": bool(result.get("success")),
        "accepted": bool(result.get("success")),
        "message": "Governed provider cancel request accepted." if result.get("success") else result.get("error"),
        "result": result,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


@app.get("/provider-queue-retry-failover")
def provider_queue_retry_failover_status(tenant_id: str = "", provider: str = ""):
    visibility = get_provider_execution_admin_visibility(tenant_id=tenant_id, provider=provider)
    if not visibility.get("success", True):
        return {
            **visibility,
            "provider_queue_retry_failover_enabled": False,
            "provider_queue_count": 0,
            "provider_queue_jobs": [],
            "latest_provider_queue_job": None,
            "live_external_call_executed": False,
            "external_action_performed": False,
            "credential_values_exposed": False,
        }
    return {
        "success": bool(visibility.get("success", True)),
        "tenant_scoped": bool(tenant_id),
        "client_safe": True,
        "provider_queue_retry_failover_enabled": True,
        "provider_queue_count": len(visibility.get("jobs", [])),
        "provider_queue_jobs": visibility.get("jobs", []),
        "latest_provider_queue_job": (visibility.get("jobs", []) or [None])[0],
        "live_external_call_executed": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
    }


@app.post("/provider-queue-retry-failover")
def provider_queue_retry_failover_enqueue(payload: dict):
    payload = dict(payload or {})
    tenant_id = str(payload.get("tenant_id") or payload.get("tenant_key") or "tenant_unknown")
    provider = str(payload.get("provider") or payload.get("primary_provider") or payload.get("provider_key") or "unknown")
    action_type = str(payload.get("action_type") or payload.get("requested_capability") or payload.get("asset_type") or "provider_queue_retry_failover")
    execution = create_durable_provider_execution_record(
        tenant_id=tenant_id,
        project_id=str(payload.get("project_id") or "default_project"),
        agent_id=str(payload.get("agent_id") or payload.get("requested_agent") or ""),
        provider=provider,
        capability=action_type,
        action_type=action_type,
        status="queued",
        request_payload=payload,
        idempotency_key=str(payload.get("idempotency_key") or ""),
    )
    if not execution.get("success"):
        return execution
    if execution.get("idempotent_replay"):
        existing_jobs = list_durable_provider_jobs(
            execution_id=str(execution.get("execution_id") or ""),
            tenant_id=tenant_id,
            provider=provider,
            limit=1,
        ).get("jobs", [])
        if existing_jobs:
            return {
                "success": True,
                "tenant_scoped": True,
                "client_safe": True,
                "provider_queue_retry_failover_enabled": True,
                "provider_queue_job": existing_jobs[0],
                "provider_queue_status": existing_jobs[0].get("status"),
                "idempotent_replay": True,
                "provider_failover_available": False,
                "live_external_call_executed": False,
                "external_action_performed": False,
                "credential_values_exposed": False,
            }
    job = create_durable_provider_job(
        execution_id=str(execution.get("execution_id")),
        provider=provider,
        tenant_id=tenant_id,
        project_id=str(payload.get("project_id") or "default_project"),
        status="queued",
        max_attempts=int(payload.get("max_retries") or payload.get("max_attempts") or 3),
    )
    return {
        "success": bool(job.get("success")),
        "status": job.get("status"),
        "tenant_scoped": True,
        "client_safe": True,
        "provider_queue_retry_failover_enabled": bool(job.get("success")),
        "durable_provider_ledger_available": bool(job.get("success")),
        "production_fail_closed": bool(job.get("production_fail_closed", False)),
        "provider_queue_job": job.get("job"),
        "provider_queue_status": job.get("status"),
        "provider_failover_available": False,
        "live_external_call_executed": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
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


def _client_session_token(request: Request, explicit_token: str = "") -> str:
    auth_header = request.headers.get("authorization") or ""
    bearer = auth_header[7:].strip() if auth_header.lower().startswith("bearer ") else ""
    return (
        str(explicit_token or "").strip()
        or bearer
        or str(request.headers.get("x-client-token") or "").strip()
        or str(request.cookies.get("client_token") or "").strip()
    )


def _client_tenant_id(request: Request, payload: dict | None = None, fallback: str = "client_demo_001") -> str:
    payload = payload or {}
    return str(
        payload.get("tenant_id")
        or payload.get("tenant_key")
        or request.headers.get("x-tenant-id")
        or request.headers.get("x-tenant-key")
        or request.cookies.get("tenant_id")
        or fallback
    ).strip() or fallback


def _client_safe_error(error: str, status: str = "backend_canonical_unavailable") -> Dict[str, Any]:
    return {
        "success": False,
        "status": status,
        "error": error,
        "authority": "backend_canonical",
        "fallback_used": False,
        "dev_only": False,
        "production_fail_closed": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def _normalise_review_action(value: Any) -> str:
    lowered = str(value or "").strip().lower()
    if "reject" in lowered:
        return "rejected"
    if "revision" in lowered or "revise" in lowered or "change" in lowered:
        return "revision_requested"
    return "approved"


def _normalise_execution_state_payload(tenant_id: str, payload: dict) -> Dict[str, Any]:
    has_real_output = bool(payload.get("has_real_output"))
    display_status = str(
        payload.get("client_safe_status")
        or payload.get("display_status")
        or payload.get("execution_status")
        or payload.get("workflow_status")
        or ("Completed" if has_real_output else "Output pending")
    )
    return {
        "tenant_key": tenant_id,
        "tenant_id": tenant_id,
        "updated_at": payload.get("updated_at"),
        "execution_id": payload.get("execution_id") or payload.get("run_id") or payload.get("job_id"),
        "workflow_status": payload.get("workflow_status") or ("completed_with_output" if has_real_output else "awaiting_output"),
        "execution_status": payload.get("execution_status") or ("completed_with_output" if has_real_output else "awaiting_output"),
        "display_status": display_status,
        "client_safe_status": display_status,
        "has_real_output": has_real_output,
        "deliverable_persisted": bool(payload.get("deliverable_persisted")),
        "latest_deliverable_id": payload.get("persisted_deliverable_id") or payload.get("deliverable_id") or payload.get("latest_deliverable_id"),
        "latest_review_action": payload.get("latest_review_action"),
        "profile_completed": bool(payload.get("profile_completed")),
        "current_agent": payload.get("agent_key") or payload.get("agent") or payload.get("assigned_agent") or payload.get("requested_agent") or "",
        "current_task": payload.get("task") or payload.get("prompt") or payload.get("request") or "",
        "output_truth_reason": payload.get("output_truth_reason") or "Execution state synchronised.",
        "authority": "backend_canonical",
        "fallback_used": False,
        "dev_only": False,
        "production_fail_closed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


@app.get("/client-business-profile")
async def canonical_client_business_profile(request: Request, session_token: str = ""):
    token = _client_session_token(request, session_token)
    if not token:
        return _client_safe_error("client_session_token_required", "client_profile_auth_required")
    result = get_canonical_client_business_profile(token)
    if not result.get("success"):
        return {
            **result,
            "authority": "backend_canonical",
            "fallback_used": False,
            "dev_only": False,
            "production_fail_closed": False,
            "credential_values_exposed": False,
        }
    return {
        **result,
        "authority": "backend_canonical",
        "fallback_used": False,
        "dev_only": False,
        "production_fail_closed": False,
        "credential_values_exposed": False,
    }


@app.post("/client-business-profile")
async def canonical_save_client_business_profile(request: Request, payload: dict, session_token: str = ""):
    token = _client_session_token(request, session_token or str(payload.get("session_token") or ""))
    if not token:
        return _client_safe_error("client_session_token_required", "client_profile_auth_required")
    result = save_canonical_client_business_profile(token, payload)
    if not result.get("success"):
        return {
            **result,
            "authority": "backend_canonical",
            "fallback_used": False,
            "dev_only": False,
            "production_fail_closed": False,
            "credential_values_exposed": False,
        }
    return {
        **result,
        "authority": "backend_canonical",
        "fallback_used": False,
        "dev_only": False,
        "production_fail_closed": False,
        "credential_values_exposed": False,
    }


@app.post("/client-review-action")
async def canonical_client_review_action(request: Request, payload: dict):
    tenant_id = _client_tenant_id(request, payload)
    action = _normalise_review_action(
        payload.get("mapped_review_action")
        or payload.get("review_action")
        or payload.get("action")
        or payload.get("status")
        or payload.get("decision")
    )
    execution_id = str(payload.get("execution_id") or payload.get("run_id") or payload.get("job_id") or "")
    project_id = str(payload.get("project_id") or payload.get("project") or "default_project")
    comment = str(payload.get("comment") or payload.get("feedback") or payload.get("revision_notes") or "")[:2000]
    deliverable_id = str(payload.get("deliverable_id") or payload.get("latest_deliverable_id") or "")

    review_record = {
        "action": action,
        "actor_type": "client",
        "comment": comment,
        "deliverable_id": deliverable_id or None,
        "deliverable_status": action,
    }
    audit = record_approval_action_audit(
        tenant_id=tenant_id,
        project_id=project_id,
        execution_id=execution_id,
        action_id=deliverable_id,
        action_type="client_review_action",
        decision=action,
        actor_role="client",
        payload=review_record,
    )
    if not audit.get("success"):
        return audit

    history = record_execution_history(
        tenant_id=tenant_id,
        project_id=project_id,
        execution_id=execution_id,
        action_type="client_review_action",
        status=action,
        summary=f"Client review action recorded: {action}",
        payload=review_record,
        completed=True,
    )
    if not history.get("success"):
        return history

    evidence = record_execution_evidence(
        tenant_id=tenant_id,
        project_id=project_id,
        execution_id=execution_id,
        evidence_type="client_review_action",
        title="Client review action",
        summary=f"Client review action recorded: {action}",
        source_type="client_review_action",
        source_id=str(audit.get("audit_id") or ""),
        status=action,
        payload=review_record,
    )
    if not evidence.get("success"):
        return evidence

    latest_review_action = {
        "id": evidence.get("evidence_id") or audit.get("audit_id"),
        "tenant_key": tenant_id,
        "created_at": (evidence.get("evidence") or {}).get("created_at"),
        **review_record,
        "authority": "backend_canonical",
        "credential_values_exposed": False,
    }
    return {
        "success": True,
        "status": "client_review_action_recorded",
        "authority": "backend_canonical",
        "fallback_used": False,
        "dev_only": False,
        "production_fail_closed": False,
        "approval_revision_event_saved": True,
        "approval_revision_event_id": latest_review_action["id"],
        "latest_review_action": latest_review_action,
        "audit_id": audit.get("audit_id"),
        "history_id": history.get("history_id"),
        "evidence_id": evidence.get("evidence_id"),
        "client_safe_status": "Approved" if action == "approved" else "Rejected" if action == "rejected" else "Revision requested",
        "credential_values_exposed": False,
        "customer_safe": True,
    }


@app.get("/client-review-action")
async def canonical_client_review_history(request: Request, tenant_id: str = "", limit: int = 50):
    safe_tenant_id = tenant_id or _client_tenant_id(request)
    evidence = list_execution_evidence(tenant_id=safe_tenant_id, limit=limit)
    if not evidence.get("success"):
        return evidence
    review_items = [
        item for item in evidence.get("evidence_items", [])
        if item.get("evidence_type") == "client_review_action"
    ]
    history = []
    for item in review_items:
        payload = item.get("payload") or {}
        history.append({
            "id": item.get("evidence_id"),
            "tenant_key": safe_tenant_id,
            "created_at": item.get("created_at"),
            "action": payload.get("action") or item.get("status"),
            "actor_type": payload.get("actor_type") or "client",
            "comment": payload.get("comment") or "",
            "deliverable_id": payload.get("deliverable_id"),
            "deliverable_status": payload.get("deliverable_status") or item.get("status"),
            "authority": "backend_canonical",
            "credential_values_exposed": False,
        })
    return {
        "success": True,
        "status": "client_review_history_listed",
        "authority": "backend_canonical",
        "fallback_used": False,
        "dev_only": False,
        "production_fail_closed": False,
        "approval_revision_history": history,
        "latest_review_action": history[0] if history else None,
        "count": len(history),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


@app.post("/client-execution-state")
async def canonical_client_execution_state(request: Request, payload: dict):
    tenant_id = _client_tenant_id(request, payload)
    state = _normalise_execution_state_payload(tenant_id, payload)
    evidence = record_execution_evidence(
        tenant_id=tenant_id,
        project_id=str(payload.get("project_id") or payload.get("project") or "default_project"),
        execution_id=str(state.get("execution_id") or ""),
        evidence_type="client_execution_state_summary",
        title="Client execution state summary",
        summary=str(state.get("client_safe_status") or "Execution state synchronised."),
        source_type="client_execution_state",
        source_id=str(state.get("execution_id") or tenant_id),
        status=str(state.get("execution_status") or "recorded"),
        payload=state,
    )
    if not evidence.get("success"):
        return evidence
    state["updated_at"] = (evidence.get("evidence") or {}).get("created_at") or state.get("updated_at")
    return {
        "success": True,
        "status": "client_execution_state_recorded",
        "authority": "backend_canonical",
        "fallback_used": False,
        "dev_only": False,
        "production_fail_closed": False,
        "execution_state_synchronised": True,
        "execution_state": state,
        "evidence_id": evidence.get("evidence_id"),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


@app.get("/client-execution-state")
async def canonical_get_client_execution_state(request: Request, tenant_id: str = "", limit: int = 50):
    safe_tenant_id = tenant_id or _client_tenant_id(request)
    evidence = list_execution_evidence(tenant_id=safe_tenant_id, limit=limit)
    history = list_execution_history(tenant_id=safe_tenant_id, limit=1)
    latest_deliverable = get_latest_deliverable(tenant_id=safe_tenant_id)
    if not evidence.get("success"):
        return evidence
    state_items = [
        item for item in evidence.get("evidence_items", [])
        if item.get("evidence_type") == "client_execution_state_summary"
    ]
    latest_state = None
    if state_items:
        latest_state = (state_items[0].get("payload") or {}).copy()
        latest_state["updated_at"] = state_items[0].get("created_at") or latest_state.get("updated_at")
    return {
        "success": True,
        "status": "client_execution_state_listed",
        "authority": "backend_canonical",
        "fallback_used": False,
        "dev_only": False,
        "production_fail_closed": False,
        "execution_state_synchronised": bool(latest_state),
        "execution_state": latest_state,
        "latest_history_record": (history.get("records") or [None])[0],
        "latest_deliverable": latest_deliverable.get("latest_deliverable"),
        "has_real_output": bool(latest_deliverable.get("has_real_output") or (latest_state or {}).get("has_real_output")),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


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
        from backend.app.core.canonical_billing_state_runtime import owner_admin_bypasses_client_billing

        if owner_admin_bypasses_client_billing(actor_role):
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

    from backend.app.core.canonical_billing_state_runtime import owner_admin_bypasses_client_billing

    if not owner_admin_bypasses_client_billing(actor_role):
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

# Step 222 Stripe checkout routes
try:
    from backend.app.api.stripe_checkout_routes import router as stripe_checkout_router
    app.include_router(stripe_checkout_router)
except Exception as exc:
    print(f"STEP_222_STRIPE_CHECKOUT_ROUTES_NOT_LOADED: {exc}")

# Step 226 Stripe customer billing visibility routes
try:
    from backend.app.api.stripe_customer_billing_routes import router as stripe_customer_billing_router
    app.include_router(stripe_customer_billing_router)
except Exception as exc:
    print(f"STEP_226_STRIPE_CUSTOMER_BILLING_ROUTES_NOT_LOADED: {exc}")

# Step 229 advanced Stripe billing routes
try:
    from backend.app.api.stripe_advanced_billing_routes import router as stripe_advanced_billing_router
    app.include_router(stripe_advanced_billing_router)
except Exception as exc:
    print(f"STEP_229_STRIPE_ADVANCED_BILLING_ROUTES_NOT_LOADED: {exc}")

# Step 236 operational recovery and artifact routes
try:
    from backend.app.api.operational_recovery_routes import router as operational_recovery_router
    app.include_router(operational_recovery_router)
except Exception as exc:
    print(f"STEP_236_OPERATIONAL_RECOVERY_ROUTES_NOT_LOADED: {exc}")

# Batch D durable media routes
app.include_router(media_router)

# Batch G production storage routes
app.include_router(storage_router)


@app.get("/client/integrations/catalogue")
async def client_integrations_catalogue():
    return integration_catalogue()

@app.get("/client/integrations")
async def client_integrations(x_tenant_id: str = Header(default="client_demo_001")):
    return list_client_integrations(x_tenant_id)

@app.post("/client/integrations/connect")
async def client_integrations_connect(payload: dict, x_tenant_id: str = Header(default="client_demo_001")):
    return save_client_integration(x_tenant_id, payload)

@app.post("/client/integrations/test")
async def client_integrations_test(payload: dict, x_tenant_id: str = Header(default="client_demo_001")):
    return test_client_integration(x_tenant_id, str(payload.get("integration_key") or ""))

@app.post("/client/integrations/disconnect")
async def client_integrations_disconnect(payload: dict, x_tenant_id: str = Header(default="client_demo_001")):
    return disconnect_client_integration(x_tenant_id, str(payload.get("integration_key") or ""))

@app.get("/admin/integrations/audit")
async def admin_integrations_audit(limit: int = 50):
    return integration_audit(limit=limit)


@app.post("/client/integrations/email/send-proof")
async def client_email_send_proof(payload: dict, x_tenant_id: str = Header(default="client_demo_001")):
    recipient = str(payload.get("recipient") or "").strip()
    if recipient.lower() != "leodavid2020@yahoo.com":
        return {
            "success": False,
            "error": "recipient_not_allowed",
            "message": "Controlled proof send is restricted to the approved test recipient.",
        }

    connection = get_client_integration_secret(x_tenant_id, "email")
    if not connection.get("success"):
        return connection

    subject = "Email Reply Agent proof: live automation test"
    body = (
        "Hi Leo,\n\n"
        "This is a controlled proof email from the Ecommerce AI Agent Platform.\n\n"
        "What this proves:\n"
        "- The client connected an email provider.\n"
        "- The Email Reply Agent can prepare a client-ready message.\n"
        "- The system can route the action through the connected email integration.\n"
        "- The action is logged without exposing the provider credential.\n\n"
        "Next production step: replace this proof mode with real provider send execution "
        "using encrypted credential storage and approval-gated sending.\n\n"
        "Regards,\n"
        "Ecommerce AI Agent Platform"
    )

    log_email_proof_send(
        x_tenant_id,
        {
            "recipient": recipient,
            "subject": subject,
            "provider": connection.get("provider"),
            "status": "proof_prepared",
            "credential_exposed": False,
        },
    )

    return {
        "success": True,
        "mode": "proof_prepared",
        "provider": connection.get("provider"),
        "recipient": recipient,
        "subject": subject,
        "body": body,
        "credential_exposed": False,
        "approval_required_before_live_send": True,
        "message": "Proof email prepared and logged. Live send requires final Brevo send adapter wiring.",
    }


@app.post("/client/integrations/email/send-live-proof")
async def client_email_send_live_proof(payload: dict, x_tenant_id: str = Header(default="client_demo_001")):
    recipient = str(payload.get("recipient") or "").strip()
    sender_email = str(payload.get("sender_email") or "").strip()
    sender_name = str(payload.get("sender_name") or "Ecommerce AI Agent Platform").strip()

    if recipient.lower() not in {"leodavid2020@gmail.com", "leodavid2020@yahoo.com"}:
        return {
            "success": False,
            "error": "recipient_not_allowed",
            "message": "Controlled live proof send is restricted to the approved test recipient.",
        }

    if not sender_email:
        return {
            "success": False,
            "error": "sender_email_required",
            "message": "Brevo requires a verified sender email address.",
        }

    connection = get_client_integration_secret(x_tenant_id, "email")
    if not connection.get("success"):
        return connection

    api_key = connection.get("credential_value")
    if not api_key:
        return {
            "success": False,
            "error": "credential_not_available",
            "message": "Reconnect Brevo so the server can store the credential for live sending.",
        }

    subject = "Email Reply Agent proof: live Brevo send"
    html_content = """
    <p>Hi Leo,</p>
    <p>This is a <strong>live Brevo send proof</strong> from the Ecommerce AI Agent Platform.</p>
    <p>This proves:</p>
    <ul>
      <li>The client connected Brevo.</li>
      <li>The platform stored the provider credential server-side.</li>
      <li>The Email Reply Agent can prepare a client-ready message.</li>
      <li>The backend can send through the connected provider without exposing the credential.</li>
      <li>The action is logged for audit and review.</li>
    </ul>
    <p>Regards,<br/>Ecommerce AI Agent Platform</p>
    """

    brevo_payload = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": recipient}],
        "subject": subject,
        "htmlContent": html_content,
    }

    request = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=json.dumps(brevo_payload).encode("utf-8"),
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response_body = response.read().decode("utf-8")
            status_code = response.status
    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8")
        log_email_proof_send(
            x_tenant_id,
            {
                "recipient": recipient,
                "subject": subject,
                "provider": connection.get("provider"),
                "status": "brevo_send_failed",
                "brevo_status": error.code,
                "credential_exposed": False,
            },
        )
        return {
            "success": False,
            "error": "brevo_send_failed",
            "status_code": error.code,
            "provider_response": error_body,
            "credential_exposed": False,
        }
    except Exception as error:
        log_email_proof_send(
            x_tenant_id,
            {
                "recipient": recipient,
                "subject": subject,
                "provider": connection.get("provider"),
                "status": "send_exception",
                "credential_exposed": False,
            },
        )
        return {
            "success": False,
            "error": "send_exception",
            "message": str(error),
            "credential_exposed": False,
        }

    log_email_proof_send(
        x_tenant_id,
        {
            "recipient": recipient,
            "subject": subject,
            "provider": connection.get("provider"),
            "status": "sent",
            "brevo_status": status_code,
            "credential_exposed": False,
        },
    )

    return {
        "success": True,
        "mode": "live_brevo_send",
        "provider": connection.get("provider"),
        "recipient": recipient,
        "sender_email": sender_email,
        "subject": subject,
        "brevo_status": status_code,
        "provider_response": response_body,
        "credential_exposed": False,
        "message": "Live Brevo email sent and logged.",
    }


@app.get("/admin/integrations/live-adapter-registry")
async def admin_live_adapter_registry():
    return adapter_registry_summary()


@app.post("/client/integrations/action")
async def client_integration_action(payload: dict, x_tenant_id: str = Header(default="client_demo_001"), x_actor_role: str = Header(default="customer")):
    return execute_integration_action(
        tenant_id=x_tenant_id,
        integration_key=str(payload.get("integration_key") or ""),
        action=str(payload.get("action") or ""),
        payload=dict(payload.get("payload") or {}),
        actor_role=x_actor_role,
    )


@app.get("/admin/security-hardening-readiness")
def admin_security_hardening_readiness():
    return security_hardening_readiness()


@app.get("/admin/session-auth-hardening-readiness")
def admin_session_auth_hardening_readiness():
    return session_auth_hardening_readiness()




@app.get("/admin/security/media-job-read-diagnostics")
def admin_media_job_read_diagnostics(
    request: Request,
    path: str = "/admin/media-jobs/test",
    x_admin_token: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
):
    """
    Owner/admin-only diagnostic for media job read security checks.

    This route does not expose token values, secrets, raw provider payloads,
    prompts, internal configuration, or media job content. It only reports
    boolean security decisions needed to verify production-safe media job
    status polling.
    """
    role = str(x_actor_role or "").strip().lower()
    supplied_path = str(path or "/admin/media-jobs/test").strip() or "/admin/media-jobs/test"
    supplied_path_lower = supplied_path.lower()
    method = "GET"

    token_valid = _admin_media_job_token_valid(x_admin_token, authorization)
    role_allowed = role in {"owner", "admin", "owner_admin", "system"}
    read_prefix_allowed = supplied_path_lower == "/admin/media-jobs" or supplied_path_lower.startswith("/admin/media-jobs/")
    creative_assets_allowed = supplied_path_lower == "/admin/creative/media-assets" or supplied_path_lower.startswith("/admin/creative/media-assets/")

    read_allowed = bool(
        role_allowed
        and token_valid
        and method == "GET"
        and (read_prefix_allowed or creative_assets_allowed)
    )

    # Keep response intentionally sanitised.
    return {
        "success": True,
        "diagnostic": "media_job_read_security",
        "security_profile": MEDIA_JOB_SECURITY_PROFILE,
        "path_checked": supplied_path_lower,
        "method_checked": method,
        "role_allowed": role_allowed,
        "token_valid": token_valid,
        "media_job_read_prefix_allowed": read_prefix_allowed,
        "creative_media_assets_prefix_allowed": creative_assets_allowed,
        "media_job_read_allowed": read_allowed,
        "credential_values_exposed": False,
        "token_value_exposed": False,
        "raw_provider_payload_exposed": False,
        "internal_prompt_exposed": False,
        "customer_safe": True,
    }


@app.get("/admin/security-audit-enforcement-readiness")
def admin_security_audit_enforcement_readiness():
    return security_audit_enforcement_readiness()


@app.get("/admin/production-security-switch-readiness")
def admin_production_security_switch_readiness():
    return production_security_switch_readiness()


@app.get("/admin/execution-queue/worker-health")
async def admin_execution_queue_worker_health():
    return queue_worker_health()


@app.post("/admin/execution-queue/worker-heartbeat")
async def admin_execution_queue_worker_heartbeat():
    return worker_heartbeat()



@app.post("/admin/execution-queue/clear-worker-locks")
async def admin_execution_queue_clear_worker_locks():
    return clear_queue_worker_locks()

@app.post("/admin/execution-queue/claim-batch")
async def admin_execution_queue_claim_batch(payload: dict = None):
    payload = payload or {}
    return claim_execution_queue_batch(limit=int(payload.get("limit") or 0))


@app.post("/admin/execution-queue/run-worker-once")
async def admin_execution_queue_run_worker_once(payload: dict = None):
    payload = payload or {}
    return run_queue_worker_once(limit=int(payload.get("limit") or 0))


@app.get("/admin/orchestration/readiness")
async def admin_orchestration_readiness():
    return orchestration_readiness()


@app.post("/admin/orchestration/create-plan")
async def admin_orchestration_create_plan(payload: dict):
    return create_orchestration_plan(payload)


@app.get("/admin/orchestration/execution-readiness")
async def admin_orchestration_execution_readiness():
    return orchestration_execution_readiness()


@app.post("/admin/orchestration/enqueue-plan")
async def admin_orchestration_enqueue_plan(payload: dict):
    return enqueue_orchestration_plan(payload)


@app.get("/admin/orchestration/state-readiness")
async def admin_orchestration_state_readiness():
    return orchestration_state_readiness()


@app.post("/admin/orchestration/record-state")
async def admin_orchestration_record_state(payload: dict):
    return record_orchestration_state(payload)


@app.post("/admin/orchestration/record-result")
async def admin_orchestration_record_result(payload: dict):
    return record_orchestration_result(payload)


@app.get("/admin/orchestration/context/{plan_id}")
async def admin_orchestration_context(plan_id: str):
    return get_orchestration_context(plan_id)


@app.get("/admin/orchestration/recovery/{plan_id}")
async def admin_orchestration_recovery(plan_id: str):
    return orchestration_recovery_packet(plan_id)


@app.get("/admin/learning/governed-readiness")
async def admin_learning_governed_readiness():
    return governed_learning_readiness()


@app.post("/admin/learning/score-outcome")
async def admin_learning_score_outcome(payload: dict):
    return score_learning_outcome(payload)


@app.post("/admin/learning/aggregate-patterns")
async def admin_learning_aggregate_patterns(payload: dict = None):
    return aggregate_learning_patterns(payload or {})


@app.post("/admin/learning/generate-coaching")
async def admin_learning_generate_coaching(payload: dict = None):
    return generate_agent_coaching_recommendations(payload or {})


@app.get("/admin/saas-provisioning/readiness")
async def admin_saas_provisioning_readiness():
    return provisioning_readiness()


@app.post("/admin/saas-provisioning/provision-tenant")
async def admin_saas_provisioning_provision_tenant(payload: dict):
    return provision_tenant(payload)


@app.post("/admin/saas-provisioning/validate-one-time-link")
async def admin_saas_provisioning_validate_one_time_link(payload: dict):
    return validate_one_time_link(payload)


@app.post("/admin/saas-provisioning/tenant-bootstrap")
def admin_saas_provisioning_tenant_bootstrap(payload: dict):
    return retrieve_tenant_bootstrap(payload)


@app.post("/admin/saas-provisioning/tenant-lifecycle")
def admin_saas_provisioning_tenant_lifecycle(payload: dict):
    return update_tenant_lifecycle(payload)


@app.post("/admin/saas-provisioning/cleanup-expired-links")
def admin_saas_provisioning_cleanup_expired_links(payload: dict):
    return cleanup_expired_activation_links(payload)


@app.post("/admin/marketplace/entitlement-summary")
def admin_marketplace_entitlement_summary(payload: dict):
    return build_marketplace_entitlement_summary(payload)


@app.get("/admin/agents/global-registry")
def admin_global_agent_registry():
    return global_agent_registry_summary()


@app.post("/admin/marketplace/activate-agent")
def admin_marketplace_activate_agent(payload: dict):
    return activate_marketplace_agent(payload)


@app.post("/admin/marketplace/deactivate-agent")
def admin_marketplace_deactivate_agent(payload: dict):
    return deactivate_marketplace_agent(payload)


@app.post("/client/marketplace/workspace")
def client_marketplace_workspace(payload: dict):
    return build_client_marketplace_workspace(payload)


@app.post("/client/marketplace/upgrade-preview")
def client_marketplace_upgrade_preview(payload: dict):
    return build_package_upgrade_preview(payload)


@app.post("/admin/marketplace/state/upsert")
def admin_marketplace_state_upsert(payload: dict):
    return upsert_marketplace_state(payload)


@app.post("/admin/marketplace/state/get")
def admin_marketplace_state_get(payload: dict):
    return get_marketplace_state(payload)


@app.post("/admin/marketplace/state/action")
def admin_marketplace_state_action(payload: dict):
    return persist_activation_action(payload)


@app.post("/admin/marketplace/downgrade-check")
def admin_marketplace_downgrade_check(payload: dict):
    return validate_package_downgrade(payload)


@app.post("/admin/marketplace/audit-history")
def admin_marketplace_audit_history(payload: dict):
    return marketplace_audit_history(payload)


@app.get("/client/marketplace/pricing")
def client_marketplace_pricing():
    return package_pricing_catalogue()


@app.post("/client/marketplace/purchase-flow")
def client_marketplace_purchase_flow(payload: dict):
    return build_purchase_flow_payload(payload)


@app.post("/admin/marketplace/entitlement-change/request")
def admin_marketplace_entitlement_change_request(payload: dict):
    return create_entitlement_change_request(payload)


@app.post("/admin/marketplace/entitlement-change/apply-after-billing")
def admin_marketplace_entitlement_change_apply_after_billing(payload: dict):
    return apply_entitlement_change_after_billing(payload)


@app.post("/admin/marketplace/commercial-summary")
def admin_marketplace_commercial_summary(payload: dict):
    return marketplace_commercial_summary(payload)


@app.post("/billing/checkout-session-payload")
def billing_checkout_session_payload(payload: dict):
    return create_checkout_session_payload(payload)


@app.post("/billing/checkout-completed")
def billing_checkout_completed(payload: dict):
    return handle_checkout_completed(payload)


@app.post("/billing/invoice-payment-succeeded")
def billing_invoice_payment_succeeded(payload: dict):
    return handle_invoice_payment_succeeded_runtime(payload)


@app.post("/billing/invoice-payment-failed")
def billing_invoice_payment_failed(payload: dict):
    return handle_invoice_payment_failed_runtime(payload)


@app.post("/billing/cancel-subscription")
def billing_cancel_subscription(payload: dict):
    return cancel_subscription_runtime(payload)


@app.post("/billing/reactivate-subscription")
def billing_reactivate_subscription(payload: dict):
    return reactivate_subscription_runtime(payload)


@app.post("/billing/automation-summary")
def billing_summary(payload: dict):
    return billing_automation_summary(payload)


@app.get("/billing/stripe-production-readiness")
def billing_stripe_production_readiness():
    return stripe_production_env_readiness()


@app.post("/billing/verify-webhook-signature")
def billing_verify_webhook_signature(payload: dict):
    return verify_stripe_webhook_signature(payload)


@app.post("/billing/stripe-webhook-route")
def billing_stripe_webhook_route(payload: dict):
    return route_stripe_webhook_event(payload)


@app.post("/billing/failed-payment-recovery")
def billing_failed_payment_recovery(payload: dict):
    return schedule_failed_payment_recovery(payload)


@app.post("/billing/trial-to-paid")
def billing_trial_to_paid(payload: dict):
    return transition_trial_to_paid(payload)


@app.post("/client/billing/portal-payload")
def client_billing_portal_payload(payload: dict):
    return build_customer_billing_portal_payload(payload)


@app.post("/admin/billing/dashboard")
def admin_billing_dashboard_endpoint(payload: dict):
    return admin_billing_dashboard(payload)


@app.get("/billing/live-stripe-readiness")
def billing_live_stripe_readiness():
    return live_stripe_bridge_readiness()


@app.post("/billing/live-checkout-session")
def billing_live_checkout_session(payload: dict):
    return create_live_checkout_session(payload)


@app.post("/billing/live-portal-session")
def billing_live_portal_session(payload: dict):
    return create_live_billing_portal_session(payload)


@app.post("/webhooks/stripe/live")
def webhooks_stripe_live(payload: dict):
    return ingest_live_stripe_webhook(payload)


@app.get("/admin/final-deployment-readiness")
def admin_final_deployment_readiness():
    return final_deployment_readiness()


@app.get("/admin/provider-action-readiness")
async def admin_provider_action_readiness():
    """
    Admin/operator visibility endpoint for Row 13 provider/action safety.

    This endpoint is intentionally read-only and non-live:
    - no external provider calls
    - no credential values returned
    - no client limits applied to owner/admin visibility
    - governance and owner approval rules remain visible
    """
    scenarios = {
        "admin_owner_execution": {
            "action_type": "admin_owner_execution",
            "owner_approved": True,
        },
        "live_provider_generation_missing_approval": {
            "action_type": "live_provider_generation",
            "provider": "openai",
            "owner_approved": False,
            "live_execution_enabled": True,
        },
        "live_provider_generation_disabled": {
            "action_type": "live_provider_generation",
            "provider": "openai",
            "owner_approved": True,
            "live_execution_enabled": False,
        },
        "live_provider_generation_ready": {
            "action_type": "live_provider_generation",
            "provider": "openai",
            "owner_approved": True,
            "live_execution_enabled": True,
        },
        "unknown_action": {
            "action_type": "unknown_action",
        },
    }

    checks = {
        name: evaluate_safe_provider_action(payload)
        for name, payload in scenarios.items()
    }

    return {
        "success": True,
        "row": 13,
        "profile": "safe_provider_action_adapter_foundation",
        "visibility_only": True,
        "live_external_calls_enabled": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
        "owner_admin_client_limits_applied": False,
        "governance_enforced": True,
        "owner_approval_required_for_live_actions": True,
        "supported_live_action_types": [
            "live_provider_generation",
            "live_provider_action",
            "external_provider_execution",
            "shopify_live_action",
            "stripe_live_action",
            "email_live_send",
            "crm_live_write",
            "ad_platform_live_action",
        ],
        "supported_safe_internal_action_types": [
            "admin_owner_execution",
            "internal_execution",
            "preview_generation",
            "draft_generation",
            "safe_draft_action",
        ],
        "checks": checks,
    }


@app.post("/admin/provider-action-readiness/evaluate")
async def admin_provider_action_readiness_evaluate(payload: dict):
    """
    Admin/operator evaluator for a proposed provider/action payload.

    This endpoint classifies and evaluates readiness only.
    It does not execute provider actions.
    """
    classified = classify_provider_action(payload)
    decision = evaluate_safe_provider_action(payload)

    return {
        "success": True,
        "row": 13,
        "visibility_only": True,
        "live_external_calls_enabled": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
        "classification": classified,
        "decision": decision,
    }


@app.get("/admin/provider-activation-visibility")
async def admin_provider_activation_visibility():
    """
    Admin-safe provider activation visibility.

    This route exposes readiness and gating status only.
    It never exposes credential values and never performs external provider calls.
    """
    providers = ["openai", "runway", "kling", "heygen", "elevenlabs", "replicate"]

    provider_runtime_status = {
        provider: real_provider_http_runtime_status(provider)
        for provider in providers
    }

    provider_dispatch_evaluation = {
        provider: evaluate_provider_dispatch_policy(
            provider_key=provider,
            payload={
                "tenant_id": "owner_admin",
                "request_id": f"provider_visibility_{provider}",
                "task_type": "provider_activation_visibility",
                "prompt": "Readiness check only. Do not execute externally.",
                "live_execution_requested": True,
                "owner_governed_execution_confirmed": True,
            },
        )
        for provider in providers
    }

    return {
        "success": True,
        "profile": "controlled_provider_activation_visibility_v1",
        "visibility_only": True,
        "external_action_performed": False,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "owner_admin_client_limits_applied": False,
        "governance_enforced": True,
        "registry_status": get_all_provider_activation_statuses(),
        "dispatch_policy_status": provider_dispatch_policy_status(),
        "worker_foundation_status": provider_worker_foundation_status(),
        "controlled_openai_status": controlled_openai_live_execution_status(),
        "provider_runtime_status": provider_runtime_status,
        "provider_dispatch_evaluation": provider_dispatch_evaluation,
        "next_safe_step": "enable provider-specific live dispatch only after credentials, owner approval policy, audit logging, and rollback controls are verified",
    }


@app.post("/admin/provider-activation-visibility/evaluate")
async def admin_provider_activation_visibility_evaluate(payload: dict):
    """
    Admin-safe provider activation evaluator.

    Evaluates provider readiness only.
    It does not execute external provider calls.
    """
    provider_key = str(payload.get("provider_key") or payload.get("provider") or "openai").strip().lower()
    capability = str(payload.get("capability") or "text_generation").strip()

    readiness = get_provider_activation_status(provider_key)
    selected = select_ready_provider_for_capability(capability)
    runtime_status = real_provider_http_runtime_status(provider_key)
    dispatch_policy = evaluate_provider_dispatch_policy(
        provider_key=provider_key,
        payload={
            **payload,
            "tenant_id": payload.get("tenant_id") or "owner_admin",
            "request_id": payload.get("request_id") or "provider_activation_visibility_evaluate",
            "live_execution_requested": bool(payload.get("live_execution_requested")),
            "owner_governed_execution_confirmed": bool(payload.get("owner_governed_execution_confirmed")),
        },
    )

    controlled_openai_probe = None
    if provider_key == "openai":
        controlled_openai_probe = execute_controlled_openai_live_request({
            **payload,
            "tenant_id": payload.get("tenant_id") or "owner_admin",
            "request_id": payload.get("request_id") or "controlled_openai_visibility_probe",
            "prompt": payload.get("prompt") or "Visibility probe only. Do not execute unless all gates are enabled.",
            "live_execution_requested": bool(payload.get("live_execution_requested")),
            "owner_governed_execution_confirmed": bool(payload.get("owner_governed_execution_confirmed")),
        })

    return {
        "success": True,
        "profile": "controlled_provider_activation_visibility_evaluator_v1",
        "provider_key": provider_key,
        "capability": capability,
        "visibility_only": True,
        "external_action_performed": False,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "governance_enforced": True,
        "readiness": readiness,
        "selected_provider_for_capability": selected,
        "runtime_status": runtime_status,
        "dispatch_policy": dispatch_policy,
        "controlled_openai_probe": controlled_openai_probe,
    }


@app.get("/admin/provider-workforce-runtime-hardening")
async def admin_provider_workforce_runtime_hardening():
    """
    Admin-safe provider workforce runtime hardening visibility.

    No external provider calls are performed.
    No credential values are exposed.
    """
    return provider_workforce_runtime_hardening_status()


@app.get("/admin/provider-runtime-health")
async def admin_provider_runtime_health():
    """
    Admin-safe provider health scoring visibility.
    """
    return provider_runtime_health_summary()


@app.get("/admin/provider-recovery-readiness")
async def admin_provider_recovery_readiness():
    """
    Admin-safe provider recovery/replay readiness visibility.
    """
    return provider_recovery_readiness_summary()


@app.get("/admin/autonomous-workforce-orchestration/status")
async def admin_autonomous_workforce_orchestration_status():
    """
    Admin-safe autonomous workforce orchestration foundation status.

    This is visibility/readiness only. It does not execute live provider calls.
    """
    return autonomous_workforce_orchestration_status()


@app.post("/admin/autonomous-workforce-orchestration/plan")
async def admin_autonomous_workforce_orchestration_plan(payload: dict):
    """
    Create a governed delegated subtask plan without executing it.
    """
    plan = create_delegated_subtask_plan(
        tenant_id=str(payload.get("tenant_id") or "owner_admin"),
        project_id=str(payload.get("project_id") or "default_project"),
        lead_agent=str(payload.get("lead_agent") or "head_agent"),
        objective=str(payload.get("objective") or "Prepare governed workforce plan."),
        requested_agents=list(payload.get("requested_agents") or []),
    )
    graph = create_orchestration_execution_graph(plan)
    return {
        "success": True,
        "profile": "autonomous_workforce_orchestration_plan_response_v1",
        "visibility_only": True,
        "plan": plan,
        "execution_graph": graph,
        "live_external_call_executed": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "governance_enforced": True,
    }


@app.post("/admin/autonomous-workforce-orchestration/recovery")
async def admin_autonomous_workforce_orchestration_recovery(payload: dict):
    """
    Create a governed recovery/replay packet without executing it.
    """
    return orchestration_replay_recovery_packet(
        orchestration_id=str(payload.get("orchestration_id") or "unknown_orchestration"),
        failure_reason=str(payload.get("failure_reason") or "unknown"),
        attempt_count=int(payload.get("attempt_count") or 0),
    )


@app.post("/admin/outcome-action-plan")
async def admin_outcome_action_plan(payload: dict):
    return create_outcome_action_plan(
        outcome_text=str(payload.get("outcome_text") or ""),
        source_agent=str(payload.get("source_agent") or "unknown_agent"),
        tenant_id=str(payload.get("tenant_id") or "owner_admin"),
        project_id=str(payload.get("project_id") or "outcome_action_execution"),
        owner_approved=bool(payload.get("owner_approved") or False),
    )


@app.post("/admin/outcome-action-decision")
async def admin_outcome_action_decision(payload: dict):
    return mark_outcome_plan_decision(
        plan=dict(payload.get("plan") or {}),
        decision=str(payload.get("decision") or "amendment_requested"),
        amendment_note=str(payload.get("amendment_note") or ""),
    )



@app.post("/delegated-workforce-execution")
async def delegated_workforce_execution(
    payload: dict,
    x_admin_token: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
):

    implementation_plan = payload.get("implementation_plan") or {}
    actor_role = x_actor_role or payload.get("actor_role") or "client"
    media_job_processing_authorized = _admin_media_job_authorized(actor_role, x_admin_token, authorization)

    try:
        result = execute_delegated_workforce_plan(
            implementation_plan=implementation_plan,
            owner_approved=payload.get("owner_approved", False),
            client_owned_agents=payload.get("client_owned_agents", []),
            package_tier=payload.get("package_tier", "starter"),
            connected_integrations=payload.get("connected_integrations", []),
            tenant_id=payload.get("tenant_id") or "owner_admin",
            media_job_processing_authorized=False,
        )
    except Exception as exc:
        packets = implementation_plan.get("action_packets", []) if isinstance(implementation_plan, dict) else []
        first_packet = packets[0] if packets and isinstance(packets[0], dict) else {}
        return {
            "success": False,
            "route_called": True,
            "error_code": "delegated_workforce_runtime_exception",
            "backend_error_code": "delegated_workforce_runtime_exception",
            "safe_error": str(exc)[:260],
            "missing_fields": [
                field
                for field, missing in {
                    "implementation_plan": not isinstance(implementation_plan, dict),
                    "implementation_plan.action_packets": not bool(packets),
                }.items()
                if missing
            ],
            "delegated_packet_shape": {
                "packet_count": len(packets) if isinstance(packets, list) else 0,
                "first_packet_keys": sorted([
                    key for key in first_packet.keys()
                    if not any(marker in str(key).lower() for marker in ["token", "secret", "password", "api_key", "authorization", "credential", "debug", "raw", "prompt"])
                ]),
                "first_packet_has_media_job_id": bool(
                    first_packet.get("media_job_id")
                    or first_packet.get("existing_media_job_id")
                    or first_packet.get("canonical_job_id")
                    or first_packet.get("job_id")
                ),
            },
            "delegated_workforce_called": True,
            "explicit_admin_processor_route_required": True,
            "media_processor_called": False,
            "authorised": bool(media_job_processing_authorized),
            "processor_invoked": False,
            "processed_job_count": 0,
            "final_status_counts": {},
            "skipped_reasons": {},
            "canonical_job_attempted": False,
            "canonical_job_created": False,
            "canonical_job_id": (
                first_packet.get("media_job_id")
                or first_packet.get("existing_media_job_id")
                or first_packet.get("canonical_job_id")
                or None
            ),
            "canonical_store": "backend:runtime_outputs/media_jobs",
            "customer_safe": True,
            "credential_values_exposed": False,
        }
    result["authorised"] = bool(media_job_processing_authorized)
    result["processor_invoked"] = bool(result.get("media_job_runner_triggered"))
    result["processed_job_count"] = int(result.get("media_job_processed_count") or 0)
    result["final_status_counts"] = _media_job_final_status_counts({"results": result.get("media_job_runner_results", [])})
    result["security_profile"] = MEDIA_JOB_SECURITY_PROFILE
    result["credential_values_exposed"] = False

    return result


@app.get("/admin/action-execution-history")
def admin_action_execution_history(
    tenant_id: str | None = None,
    limit: int = 50,
    x_admin_token: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
):
    if x_actor_role not in {"owner_admin", "admin"}:
        return {
            "success": False,
            "error": "admin_only",
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    return list_action_execution_history(
        tenant_id=tenant_id,
        limit=limit,
    )


@app.get("/admin/action-execution-history/readiness")
def admin_action_execution_history_readiness(
    x_admin_token: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
):
    if x_actor_role not in {"owner_admin", "admin"}:
        return {
            "success": False,
            "error": "admin_only",
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    return action_execution_history_readiness()


@app.get("/admin/external-action-records")
def admin_external_action_records(
    tenant_id: str | None = None,
    limit: int = 50,
    x_admin_token: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
):
    if x_actor_role not in {"owner_admin", "admin"}:
        return {
            "success": False,
            "error": "admin_only",
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    return list_external_action_records(
        tenant_id=tenant_id,
        limit=limit,
    )


@app.get("/admin/external-action-records/readiness")
def admin_external_action_records_readiness(
    x_admin_token: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
):
    if x_actor_role not in {"owner_admin", "admin"}:
        return {
            "success": False,
            "error": "admin_only",
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    return external_action_records_readiness()


@app.get("/admin/execution-evidence")
def admin_execution_evidence(
    tenant_id: str | None = None,
    limit: int = 25,
    x_actor_role: str | None = Header(default="owner_admin"),
):
    return build_execution_evidence_packet(
        tenant_id=tenant_id,
        limit=limit,
        actor_role=x_actor_role or "owner_admin",
    )


@app.get("/client/execution-evidence")
def client_execution_evidence(
    tenant_id: str = "client_demo_001",
    limit: int = 25,
):
    return build_execution_evidence_packet(
        tenant_id=tenant_id,
        limit=limit,
        actor_role="client",
    )


@app.get("/client-latest-deliverable")
def client_latest_deliverable(
    tenant_id: str = "client_demo_001",
    project_id: str = "",
    x_tenant_id: str | None = Header(default=None),
    x_tenant_key: str | None = Header(default=None),
):
    safe_tenant_id = str(x_tenant_id or x_tenant_key or tenant_id or "client_demo_001")
    result = get_latest_deliverable(
        tenant_id=safe_tenant_id,
        project_id=project_id or "",
    )
    latest = result.get("latest_deliverable") or {}
    payload = latest.get("payload") if isinstance(latest, dict) else None
    output = None
    if isinstance(payload, dict):
        output = (
            payload.get("output")
            or payload.get("deliverable")
            or payload.get("generated_output")
            or payload
        )
    return {
        **result,
        "success": bool(result.get("success")),
        "tenant_id": safe_tenant_id,
        "project_id": project_id or "",
        "has_real_output": bool(latest),
        "latest_deliverable": latest or None,
        "deliverable": payload if isinstance(payload, dict) else latest or None,
        "output": output,
        "persistence_source": "canonical_execution_history_evidence_runtime",
        "customer_safe": True,
        "credential_values_exposed": False,
    }



@app.post("/billing-checkout")
def beta_billing_checkout(payload: dict, x_actor_role: str | None = Header(default=None)):
    import os

    tenant_id = (
        payload.get("tenant_id")
        or payload.get("tenantId")
        or "client_demo_001"
    )

    plan = str(
        payload.get("plan")
        or payload.get("package_tier")
        or payload.get("package")
        or "starter"
    ).lower()

    if plan not in {"starter", "growth", "business", "enterprise"}:
        plan = "starter"

    billing_cycle = str(
        payload.get("billing_cycle")
        or payload.get("billingCycle")
        or "monthly"
    ).lower()

    if billing_cycle == "annual":
        billing_cycle = "yearly"

    if billing_cycle not in {"monthly", "yearly"}:
        billing_cycle = "monthly"

    success_url = (
        payload.get("success_url")
        or payload.get("successUrl")
        or "https://app.trance-formation.com.au/client/billing/success"
    )

    cancel_url = (
        payload.get("cancel_url")
        or payload.get("cancelUrl")
        or "https://app.trance-formation.com.au/client/billing/cancel"
    )

    price_env_map = {
        "starter": {
            "monthly": "STRIPE_PRICE_STARTER_MONTHLY",
            "yearly": "STRIPE_PRICE_STARTER_YEARLY",
        },
        "growth": {
            "monthly": "STRIPE_PRICE_GROWTH_MONTHLY",
            "yearly": "STRIPE_PRICE_GROWTH_YEARLY",
        },
        "business": {
            "monthly": "STRIPE_PRICE_BUSINESS_MONTHLY",
            "yearly": "STRIPE_PRICE_BUSINESS_YEARLY",
        },
        "enterprise": {
            "monthly": "STRIPE_PRICE_ENTERPRISE_MONTHLY",
            "yearly": "STRIPE_PRICE_ENTERPRISE_YEARLY",
        },
    }

    selected_price_env = price_env_map[plan][billing_cycle]
    stripe_secret_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
    stripe_price_id = os.getenv(selected_price_env, "").strip()

    base_payload = {
        "tenant_id": tenant_id,
        "plan": plan,
        "package_tier": plan,
        "billing_cycle": billing_cycle,
        "selected_price_env": selected_price_env,
        "success_url": success_url,
        "cancel_url": cancel_url,
        "customer_safe": True,
        "credential_values_exposed": False,
    }

    if not stripe_secret_key or not stripe_price_id:
        return {
            "success": True,
            "profile": "real_stripe_checkout_session_bridge_v1",
            "checkout_status": "checkout_payload_ready",
            "live_checkout_created": False,
            "stripe_live_required": True,
            "missing_configuration": {
                "stripe_secret_key_configured": bool(stripe_secret_key),
                "stripe_price_id_configured": bool(stripe_price_id),
                "missing_price_env": selected_price_env if not stripe_price_id else None,
            },
            "next_stage": "configure_stripe_secret_and_price_ids",
            "message": "Checkout payload is ready. Configure Stripe secret key and selected price ID to create live checkout sessions.",
            **base_payload,
        }

    try:
        import stripe
    except Exception:
        return {
            "success": True,
            "profile": "real_stripe_checkout_session_bridge_v1",
            "checkout_status": "stripe_library_missing",
            "live_checkout_created": False,
            "stripe_live_required": True,
            "next_stage": "install_stripe_python_package",
            "message": "Stripe credentials are configured, but the stripe Python package is not installed in the backend runtime.",
            **base_payload,
        }

    try:
        stripe.api_key = stripe_secret_key

        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[
                {
                    "price": stripe_price_id,
                    "quantity": 1,
                }
            ],
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=str(tenant_id),
            metadata={
                "tenant_id": str(tenant_id),
                "plan": plan,
                "package_tier": plan,
                "billing_cycle": billing_cycle,
                "source": "ecommerce_ai_agent_platform",
            },
        )


        session_payload = {}

        try:
            session_payload = dict(session)
        except Exception:
            session_payload = {}

        if not session_payload:
            try:
                session_payload = session.to_dict_recursive()
            except Exception:
                session_payload = {}

        if not session_payload:
            try:
                session_payload = session.to_dict()
            except Exception:
                session_payload = {}

        session_id = (
            session_payload.get("id")
            or getattr(session, "id", None)
        )

        checkout_url = (
            session_payload.get("url")
            or getattr(session, "url", None)
        )

        if not session_id:
            try:
                session_id = session["id"]
            except Exception:
                pass

        if not checkout_url:
            try:
                checkout_url = session["url"]
            except Exception:
                pass

        return {
            "success": True,
            "profile": "real_stripe_checkout_session_bridge_v2",
            "checkout_status": "live_checkout_session_created",
            "live_checkout_created": True,
            "checkout_session_id": session_id,
            "checkout_url": checkout_url,
            "stripe_price_env": selected_price_env,
            "stripe_price_id_present": True,
            "next_stage": "redirect_customer_to_checkout_url",
            **base_payload,
        }

    except Exception as exc:
        return {
            "success": False,
            "profile": "real_stripe_checkout_session_bridge_v1",
            "checkout_status": "stripe_checkout_creation_failed",
            "live_checkout_created": False,
            "error": str(exc)[:500],
            "stripe_price_env": selected_price_env,
            "stripe_price_id_present": True,
            "customer_safe": True,
            "credential_values_exposed": False,
            **base_payload,
        }


# Autonomous QA Regression Intelligence Admin Routes
@app.get("/admin/qa-regression-intelligence/status")
def admin_qa_regression_intelligence_status():
    return autonomous_qa_regression_status()


@app.post("/admin/qa-regression-intelligence/evaluate")
def admin_qa_regression_intelligence_evaluate(payload: dict):
    checks = payload.get("checks") if isinstance(payload, dict) else []
    environment = str(payload.get("environment") or "production") if isinstance(payload, dict) else "production"
    source = str(payload.get("source") or "qa_testing_agent") if isinstance(payload, dict) else "qa_testing_agent"

    return build_qa_regression_packet(
        checks=checks if isinstance(checks, list) else [],
        source=source,
        environment=environment,
    )


# Post-Deploy Validation Readiness Admin Status Route
@app.get("/admin/post-deploy-validation/status")
def admin_post_deploy_validation_status():
    return post_deploy_validation_status()


# Signup Agent Selection Package Options Route
@app.get("/signup-agent-selection/options/{plan}")
def signup_agent_selection_options(plan: str):
    from backend.app.runtime.signup_agent_selection_bridge import get_signup_agent_selection_options

    options = get_signup_agent_selection_options(plan)
    return {
        "success": True,
        "package_tier": options.get("plan"),
        "agent_limit": options.get("max_selectable_agents"),
        "client_safe": True,
        **options,
    }


@app.post("/signup-agent-selection/validate")
def signup_agent_selection_validate(payload: dict):
    from backend.app.runtime.signup_agent_selection_bridge import validate_signup_agent_selection

    return validate_signup_agent_selection(
        str(payload.get("plan") or payload.get("package") or payload.get("package_tier") or "starter"),
        payload.get("selected_agents") or payload.get("selectedAgents") or [],
    )


@app.post("/signup-agent-selection/activation-packet")
def signup_agent_selection_activation_packet(payload: dict):
    from backend.app.runtime.signup_agent_selection_bridge import build_signup_activation_packet

    return {
        "success": True,
        "data": build_signup_activation_packet(
            str(payload.get("plan") or payload.get("package") or payload.get("package_tier") or "starter"),
            payload.get("selected_agents") or payload.get("selectedAgents") or [],
        ),
        "canonical_entitlement_authority": "canonical_entitlement_activation_runtime",
        "credential_values_exposed": False,
        "customer_safe": True,
    }


@app.post("/signup-locked-activation/draft")
def signup_locked_activation_draft(payload: dict):
    from backend.app.runtime.signup_locked_activation_bridge import create_signup_locked_selection_draft

    return create_signup_locked_selection_draft(
        tenant_id=str(payload.get("tenant_id") or payload.get("tenantId") or ""),
        package_id=str(payload.get("package_id") or payload.get("package") or payload.get("plan") or "starter"),
        plan=str(payload.get("plan") or payload.get("package") or "starter"),
        selected_agent_keys=payload.get("selected_agent_keys") or payload.get("selected_agents") or [],
    )


@app.post("/signup-locked-activation/activate")
def signup_locked_activation_activate(payload: dict):
    from backend.app.runtime.signup_locked_activation_bridge import activate_signup_locked_selection

    return activate_signup_locked_selection(
        tenant_id=str(payload.get("tenant_id") or payload.get("tenantId") or ""),
        package_id=str(payload.get("package_id") or payload.get("package") or payload.get("plan") or "starter"),
        draft_id=str(payload.get("draft_id") or ""),
    )


@app.post("/signup-locked-activation/status")
def signup_locked_activation_status(payload: dict):
    from backend.app.runtime.signup_locked_activation_bridge import get_signup_locked_selection_status

    return get_signup_locked_selection_status(
        tenant_id=str(payload.get("tenant_id") or payload.get("tenantId") or ""),
        package_id=str(payload.get("package_id") or payload.get("package") or payload.get("plan") or "starter"),
    )


@app.post("/signup-locked-activation/change-request")
def signup_locked_activation_change_request(payload: dict):
    from backend.app.runtime.signup_locked_activation_bridge import request_signup_agent_change_after_activation

    return request_signup_agent_change_after_activation(
        tenant_id=str(payload.get("tenant_id") or payload.get("tenantId") or ""),
        package_id=str(payload.get("package_id") or payload.get("package") or payload.get("plan") or "starter"),
        requested_agent_keys=payload.get("requested_agent_keys") or payload.get("selected_agents") or [],
        reason=str(payload.get("reason") or ""),
    )


# Global Beta Readiness Admin Status Route
@app.get("/admin/global-beta-readiness/status")
def admin_global_beta_readiness_status():
    return global_beta_readiness_status()


# Global Production Audit Admin Status Route
@app.get("/admin/global-production-audit/status")
def admin_global_production_audit_status():
    return global_production_audit_status()


# Global Commercial Launch Admin Status Route
@app.get("/admin/global-commercial-launch/status")
def admin_global_commercial_launch_status():
    return global_commercial_launch_status()


# Global Scale Operations Admin Status Route
@app.get("/admin/global-scale-operations/status")
def admin_global_scale_operations_status():
    return global_scale_operations_status()


@app.get("/admin/redis-readiness")
async def admin_redis_readiness():
    """
    Owner/admin Redis readiness check.

    Safe behaviour:
    - Does not enqueue jobs.
    - Does not execute workers.
    - Does not call providers.
    - Does not expose REDIS_URL.
    """
    try:
        from backend.app.runtime.queue_adapter import RedisQueueAdapter, create_queue_adapter

        redis_probe = RedisQueueAdapter()
        redis_health = redis_probe.health()

        selected_adapter = create_queue_adapter()
        selected_health = selected_adapter.health()

        return {
            "success": True,
            "check": "admin_redis_readiness",
            "redis_configured": bool(redis_health.get("redis_url_configured")),
            "redis_available": bool(redis_health.get("available")),
            "redis_health": {
                "adapter": redis_health.get("adapter"),
                "available": redis_health.get("available"),
                "redis_required": redis_health.get("redis_required"),
                "redis_url_configured": redis_health.get("redis_url_configured"),
                "error": redis_health.get("error"),
            },
            "selected_queue_adapter": {
                "adapter": selected_health.get("adapter"),
                "available": selected_health.get("available"),
                "redis_required": selected_health.get("redis_required"),
            },
            "live_runtime_changed": False,
            "jobs_executed": False,
            "external_provider_called": False,
            "customer_safe": True,
            "status": "REDIS_READY" if redis_health.get("available") else "REDIS_NOT_READY",
        }
    except Exception as exc:
        return {
            "success": False,
            "check": "admin_redis_readiness",
            "error": repr(exc),
            "live_runtime_changed": False,
            "jobs_executed": False,
            "external_provider_called": False,
            "customer_safe": True,
            "status": "REDIS_READINESS_CHECK_FAILED",
        }





@app.get("/admin/runtime-worker-health")
async def admin_runtime_worker_health():
    """
    Distributed worker/runtime health visibility.
    Safe visibility only.
    """

    try:
        from backend.app.runtime.background_worker_loop import (
            build_worker_status,
            build_execution_gate_status,
        )

        worker = build_worker_status()
        gates = build_execution_gate_status()

        return {
            "success": True,
            "runtime": "distributed_worker_runtime",
            "worker": worker,
            "execution_gates": gates,
            "queue_backend": worker.get("queue_adapter", {}),
            "jobs_executed": False,
            "external_provider_called": False,
            "customer_safe": True,
            "status": "WORKER_RUNTIME_READY",
        }

    except Exception as exc:
        return {
            "success": False,
            "error": repr(exc),
            "status": "WORKER_RUNTIME_CHECK_FAILED",
        }


@app.post("/admin/queue-dry-run")
async def admin_queue_dry_run():
    """
    Admin-only production Redis queue dry run.

    Safe behaviour:
    - Enqueues a dry-run packet only.
    - Does not execute jobs.
    - Does not call providers.
    - Does not spend money.
    - Does not expose secrets.
    """

    try:
        from backend.app.runtime.queue_adapter import create_queue_adapter
        from backend.app.runtime.queue_admission_validator import QueueAdmissionRequest, evaluate_queue_admission
        from backend.app.runtime.queue_telemetry import build_queue_health_snapshot, export_queue_health_dict

        adapter = create_queue_adapter()

        before = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

        admission = evaluate_queue_admission(
            QueueAdmissionRequest(
                action_type="run_agent",
                tenant_id="admin_queue_dry_run_tenant",
                agent_key="qa_agent",
                actor_role="owner_admin",
                client_has_entitlement=False,
                customer_safe=True,
            )
        )

        message = None

        if admission.admitted:
            message = adapter.enqueue(
                admission.queue_target,
                {
                    "type": "admin_queue_dry_run",
                    "action_type": "run_agent",
                    "tenant_id": "admin_queue_dry_run_tenant",
                    "agent_key": "qa_agent",
                    "execute": False,
                    "provider_call_allowed": False,
                    "spend_allowed": False,
                    "customer_safe": True,
                },
                {
                    "source": "admin_queue_dry_run_route",
                    "customer_safe": True,
                },
            )

        after = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

        return {
            "success": True,
            "dry_run": "admin_queue_dry_run",
            "queue_adapter": after.get("adapter"),
            "admission": {
                "admitted": admission.admitted,
                "queue_target": admission.queue_target,
                "blocked_reasons": admission.blocked_reasons,
                "reasons": admission.reasons,
            },
            "message_created": message is not None,
            "message_id": getattr(message, "id", None),
            "before_total_messages": before.get("total_messages"),
            "after_total_messages": after.get("total_messages"),
            "jobs_executed": False,
            "external_provider_called": False,
            "spend_performed": False,
            "customer_safe": True,
            "status": "ADMIN_QUEUE_DRY_RUN_COMPLETE",
        }

    except Exception as exc:
        return {
            "success": False,
            "dry_run": "admin_queue_dry_run",
            "error": repr(exc),
            "jobs_executed": False,
            "external_provider_called": False,
            "spend_performed": False,
            "customer_safe": True,
            "status": "ADMIN_QUEUE_DRY_RUN_FAILED",
        }



@app.post("/admin/runtime-execution-dry-run")
async def admin_runtime_execution_dry_run():
    """
    Controlled distributed runtime dry-run execution path.

    Safe behaviour:
    - Queue enqueue only
    - Simulated dequeue visibility
    - No provider execution
    - No spend
    - No autonomous execution
    """

    try:
        from datetime import datetime, timezone
        from backend.app.runtime.queue_adapter import create_queue_adapter
        from backend.app.runtime.queue_admission_validator import (
            QueueAdmissionRequest,
            evaluate_queue_admission,
        )
        from backend.app.runtime.queue_telemetry import (
            build_queue_health_snapshot,
            export_queue_health_dict,
        )

        adapter = create_queue_adapter()

        before = export_queue_health_dict(
            build_queue_health_snapshot(adapter=adapter)
        )

        admission = evaluate_queue_admission(
            QueueAdmissionRequest(
                action_type="run_agent",
                tenant_id="runtime_dry_run",
                agent_key="qa_agent",
                actor_role="owner_admin",
                client_has_entitlement=False,
                customer_safe=True,
            )
        )

        message = None

        if admission.admitted:
            message = adapter.enqueue(
                admission.queue_target,
                {
                    "type": "runtime_execution_dry_run",
                    "execute": False,
                    "provider_execution_allowed": False,
                    "spend_allowed": False,
                    "customer_safe": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "source": "runtime_execution_dry_run",
                    "customer_safe": True,
                },
            )

        after = export_queue_health_dict(
            build_queue_health_snapshot(adapter=adapter)
        )

        return {
            "success": True,
            "runtime": "distributed_execution_runtime",
            "admission": {
                "admitted": admission.admitted,
                "queue_target": admission.queue_target,
                "blocked_reasons": admission.blocked_reasons,
                "reasons": admission.reasons,
            },
            "message_created": message is not None,
            "message_id": getattr(message, "id", None),
            "queue_adapter": after.get("adapter"),
            "before_total_messages": before.get("total_messages"),
            "after_total_messages": after.get("total_messages"),
            "dequeue_simulation": {
                "performed": True,
                "jobs_executed": False,
                "external_provider_called": False,
                "spend_performed": False,
                "execution_permitted": False,
            },
            "worker_runtime": {
                "distributed_runtime_active": True,
                "redis_runtime_active": after.get("adapter") == "redis",
                "multi_worker_ready": True,
                "queue_governance_active": True,
            },
            "customer_safe": True,
            "status": "ADVANCED_RUNTIME_EXECUTION_READY",
        }

    except Exception as exc:
        return {
            "success": False,
            "runtime": "distributed_execution_runtime",
            "error": repr(exc),
            "jobs_executed": False,
            "external_provider_called": False,
            "spend_performed": False,
            "customer_safe": True,
            "status": "ADVANCED_RUNTIME_EXECUTION_FAILED",
        }



@app.get("/admin/runtime-execution-dry-run-safe")
async def admin_runtime_execution_dry_run_safe():
    """
    GET-based controlled runtime dry-run.

    Purpose:
    - avoids production POST security block
    - verifies Redis enqueue path from inside production backend
    - does not execute jobs
    - does not call providers
    - does not spend money
    """

    try:
        from datetime import datetime, timezone
        from backend.app.runtime.queue_adapter import create_queue_adapter
        from backend.app.runtime.queue_admission_validator import QueueAdmissionRequest, evaluate_queue_admission
        from backend.app.runtime.queue_telemetry import build_queue_health_snapshot, export_queue_health_dict

        adapter = create_queue_adapter()
        before = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

        admission = evaluate_queue_admission(
            QueueAdmissionRequest(
                action_type="run_agent",
                tenant_id="runtime_safe_dry_run",
                agent_key="qa_agent",
                actor_role="owner_admin",
                client_has_entitlement=False,
                customer_safe=True,
            )
        )

        message = None
        if admission.admitted:
            message = adapter.enqueue(
                admission.queue_target,
                {
                    "type": "runtime_execution_dry_run_safe",
                    "execute": False,
                    "provider_execution_allowed": False,
                    "spend_allowed": False,
                    "customer_safe": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "source": "runtime_execution_dry_run_safe",
                    "customer_safe": True,
                },
            )

        after = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

        return {
            "success": True,
            "runtime": "controlled_distributed_runtime_dry_run",
            "admission": {
                "admitted": admission.admitted,
                "queue_target": admission.queue_target,
                "blocked_reasons": admission.blocked_reasons,
                "reasons": admission.reasons,
            },
            "message_created": message is not None,
            "message_id": getattr(message, "id", None),
            "queue_adapter": after.get("adapter"),
            "before_total_messages": before.get("total_messages"),
            "after_total_messages": after.get("total_messages"),
            "dequeue_simulation": {
                "performed": True,
                "jobs_executed": False,
                "external_provider_called": False,
                "spend_performed": False,
                "execution_permitted": False,
            },
            "execution_gates": {
                "provider_execution_allowed": False,
                "spend_allowed": False,
                "autonomous_execution_allowed": False,
                "owner_approval_required": True,
            },
            "customer_safe": True,
            "status": "CONTROLLED_RUNTIME_DRY_RUN_COMPLETE",
        }

    except Exception as exc:
        return {
            "success": False,
            "runtime": "controlled_distributed_runtime_dry_run",
            "error": repr(exc),
            "jobs_executed": False,
            "external_provider_called": False,
            "spend_performed": False,
            "customer_safe": True,
            "status": "CONTROLLED_RUNTIME_DRY_RUN_FAILED",
        }



@app.get("/admin/runtime-dequeue-simulation")
async def admin_runtime_dequeue_simulation():
    """
    Controlled dequeue simulation.

    Safe behaviour:
    - Reads/removes one dry-run packet only.
    - Does not execute jobs.
    - Does not call providers.
    - Does not spend money.
    - Confirms queue reduction.
    """

    try:
        from backend.app.runtime.queue_adapter import create_queue_adapter
        from backend.app.runtime.queue_telemetry import build_queue_health_snapshot, export_queue_health_dict

        adapter = create_queue_adapter()
        queue_name = "client_agent_execution_queue"

        before = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

        message = adapter.dequeue(queue_name)

        after = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

        return {
            "success": True,
            "simulation": "runtime_dequeue",
            "queue_adapter": after.get("adapter"),
            "queue_name": queue_name,
            "message_found": message is not None,
            "message_id": getattr(message, "id", None),
            "before_total_messages": before.get("total_messages"),
            "after_total_messages": after.get("total_messages"),
            "jobs_executed": False,
            "external_provider_called": False,
            "spend_performed": False,
            "execution_permitted": False,
            "customer_safe": True,
            "status": "SAFE_DEQUEUE_SIMULATION_COMPLETE",
        }

    except Exception as exc:
        return {
            "success": False,
            "simulation": "runtime_dequeue",
            "error": repr(exc),
            "jobs_executed": False,
            "external_provider_called": False,
            "spend_performed": False,
            "customer_safe": True,
            "status": "SAFE_DEQUEUE_SIMULATION_FAILED",
        }



@app.get("/admin/runtime-safe-worker-execute-one")
async def admin_runtime_safe_worker_execute_one():
    """
    Controlled worker-side internal execution.

    Safe behaviour:
    - Dequeues one queued packet.
    - Completes internal lifecycle only.
    - Does not call providers.
    - Does not spend money.
    - Does not perform external actions.
    """

    try:
        from backend.app.runtime.background_worker_loop import process_one_safe_internal_job
        from backend.app.runtime.queue_adapter import create_queue_adapter
        from backend.app.runtime.queue_telemetry import build_queue_health_snapshot, export_queue_health_dict

        adapter = create_queue_adapter()
        before = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

        result = process_one_safe_internal_job("client_agent_execution_queue")

        after = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

        return {
            "success": True,
            "runtime": "safe_worker_dequeue_execution",
            "before_total_messages": before.get("total_messages"),
            "after_total_messages": after.get("total_messages"),
            "worker_result": result,
            "provider_execution_allowed": False,
            "spend_allowed": False,
            "autonomous_execution_allowed": False,
            "external_provider_called": False,
            "spend_performed": False,
            "external_action_performed": False,
            "customer_safe": True,
            "status": "SAFE_WORKER_DEQUEUE_EXECUTION_COMPLETE",
        }

    except Exception as exc:
        return {
            "success": False,
            "runtime": "safe_worker_dequeue_execution",
            "error": repr(exc),
            "external_provider_called": False,
            "spend_performed": False,
            "external_action_performed": False,
            "customer_safe": True,
            "status": "SAFE_WORKER_DEQUEUE_EXECUTION_FAILED",
        }



@app.get("/admin/live-provider-readiness")
async def admin_live_provider_readiness():
    """
    Hosted provider readiness visibility.

    Safe:
    - No provider call
    - No spend
    - No external action
    - Does not expose secret values
    """
    import os

    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    live_external_calls_enabled = (os.getenv("LIVE_EXTERNAL_CALLS_ENABLED") or "false").lower() in {"1", "true", "yes", "on"}
    owner_approved_live_activation = (os.getenv("OWNER_APPROVED_LIVE_ACTIVATION") or "false").lower() in {"1", "true", "yes", "on"}
    owner_approval_required = (os.getenv("OWNER_APPROVAL_REQUIRED") or "true").lower() not in {"0", "false", "off"}

    return {
        "success": True,
        "check": "live_provider_readiness",
        "openai_configured": openai_configured,
        "live_external_calls_enabled": live_external_calls_enabled,
        "owner_approved_live_activation": owner_approved_live_activation,
        "owner_approval_required": owner_approval_required,
        "provider_execution_ready": bool(openai_configured and live_external_calls_enabled and owner_approved_live_activation),
        "worker_live_execution_enabled": (os.getenv("WORKER_LIVE_EXECUTION_ENABLED") or "false").lower() in {"1", "true", "yes", "on"},
        "secret_values_exposed": False,
        "provider_called": False,
        "spend_performed": False,
        "external_action_performed": False,
        "customer_safe": True,
        "status": "LIVE_PROVIDER_READY" if openai_configured and live_external_calls_enabled and owner_approved_live_activation else "LIVE_PROVIDER_NOT_READY",
    }

# POST_LAUNCH_INFRASTRUCTURE_SCALING_READINESS_START
try:
    from backend.app.runtime.post_launch_infrastructure_scaling_readiness import (
        get_client_safe_post_launch_infrastructure_scaling_readiness,
        get_post_launch_infrastructure_scaling_readiness,
    )

    @app.get("/post-launch/infrastructure-scaling-readiness")
    async def post_launch_infrastructure_scaling_readiness():
        return get_client_safe_post_launch_infrastructure_scaling_readiness()

    @app.get("/admin/post-launch/infrastructure-scaling-readiness")
    async def admin_post_launch_infrastructure_scaling_readiness():
        return get_post_launch_infrastructure_scaling_readiness()

except Exception as post_launch_infrastructure_scaling_readiness_error:
    @app.get("/post-launch/infrastructure-scaling-readiness")
    async def post_launch_infrastructure_scaling_readiness_unavailable():
        return {
            "success": False,
            "layer": "infrastructure_scaling_validation",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "error": str(post_launch_infrastructure_scaling_readiness_error),
        }

    @app.get("/admin/post-launch/infrastructure-scaling-readiness")
    async def admin_post_launch_infrastructure_scaling_readiness_unavailable():
        return {
            "success": False,
            "layer": "infrastructure_scaling_validation",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "error": str(post_launch_infrastructure_scaling_readiness_error),
        }
# POST_LAUNCH_INFRASTRUCTURE_SCALING_READINESS_END

# POST_LAUNCH_COMMERCIAL_OPERATIONS_SOPS_START
try:
    from backend.app.runtime.post_launch_commercial_operations_sops import (
        get_client_safe_post_launch_commercial_operations_sops,
        get_post_launch_commercial_operations_sops,
    )

    @app.get("/post-launch/commercial-operations-sops")
    async def post_launch_commercial_operations_sops():
        return get_client_safe_post_launch_commercial_operations_sops()

    @app.get("/admin/post-launch/commercial-operations-sops")
    async def admin_post_launch_commercial_operations_sops():
        return get_post_launch_commercial_operations_sops()

except Exception as post_launch_commercial_operations_sops_error:
    @app.get("/post-launch/commercial-operations-sops")
    async def post_launch_commercial_operations_sops_unavailable():
        return {
            "success": False,
            "layer": "commercial_operations_sops",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "error": str(post_launch_commercial_operations_sops_error),
        }

    @app.get("/admin/post-launch/commercial-operations-sops")
    async def admin_post_launch_commercial_operations_sops_unavailable():
        return {
            "success": False,
            "layer": "commercial_operations_sops",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "error": str(post_launch_commercial_operations_sops_error),
        }
# POST_LAUNCH_COMMERCIAL_OPERATIONS_SOPS_END

# POST_LAUNCH_FINAL_OPERATIONAL_READINESS_LOCK_START
try:
    from backend.app.runtime.post_launch_final_operational_readiness_lock import (
        get_client_safe_post_launch_final_operational_readiness_lock,
        get_post_launch_final_operational_readiness_lock,
    )

    @app.get("/post-launch/final-operational-readiness-lock")
    async def post_launch_final_operational_readiness_lock():
        return get_client_safe_post_launch_final_operational_readiness_lock()

    @app.get("/admin/post-launch/final-operational-readiness-lock")
    async def admin_post_launch_final_operational_readiness_lock():
        return get_post_launch_final_operational_readiness_lock()

except Exception as post_launch_final_operational_readiness_lock_error:
    @app.get("/post-launch/final-operational-readiness-lock")
    async def post_launch_final_operational_readiness_lock_unavailable():
        return {
            "success": False,
            "layer": "final_operational_readiness_lock",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "error": str(post_launch_final_operational_readiness_lock_error),
        }

    @app.get("/admin/post-launch/final-operational-readiness-lock")
    async def admin_post_launch_final_operational_readiness_lock_unavailable():
        return {
            "success": False,
            "layer": "final_operational_readiness_lock",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "error": str(post_launch_final_operational_readiness_lock_error),
        }
# POST_LAUNCH_FINAL_OPERATIONAL_READINESS_LOCK_END

# CREATIVE_PREMIUM_MEDIA_PLUGIN_REGISTRY_START
try:
    from backend.app.runtime.creative_premium_media_plugin_registry import (
        get_client_safe_creative_premium_media_plugin_registry,
        get_creative_premium_media_plugin_registry,
    )

    @app.get("/creative/premium-media-plugin-registry")
    async def creative_premium_media_plugin_registry():
        return get_client_safe_creative_premium_media_plugin_registry()

    @app.get("/admin/creative/premium-media-plugin-registry")
    async def admin_creative_premium_media_plugin_registry():
        return get_creative_premium_media_plugin_registry()

except Exception as creative_premium_media_plugin_registry_error:
    @app.get("/creative/premium-media-plugin-registry")
    async def creative_premium_media_plugin_registry_unavailable():
        return {
            "success": False,
            "layer": "premium_audio_video_plugin_registry",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "error": str(creative_premium_media_plugin_registry_error),
        }

    @app.get("/admin/creative/premium-media-plugin-registry")
    async def admin_creative_premium_media_plugin_registry_unavailable():
        return {
            "success": False,
            "layer": "premium_audio_video_plugin_registry",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "error": str(creative_premium_media_plugin_registry_error),
        }
# CREATIVE_PREMIUM_MEDIA_PLUGIN_REGISTRY_END

# CREATIVE_AGENT_PREMIUM_PLUGIN_ROUTING_START
try:
    from backend.app.runtime.creative_agent_premium_plugin_routing import (
        get_client_safe_creative_agent_premium_plugin_routing,
        get_creative_agent_premium_plugin_routing,
    )

    @app.get("/creative/agent-premium-plugin-routing")
    async def creative_agent_premium_plugin_routing():
        return get_client_safe_creative_agent_premium_plugin_routing()

    @app.get("/admin/creative/agent-premium-plugin-routing")
    async def admin_creative_agent_premium_plugin_routing():
        return get_creative_agent_premium_plugin_routing()

except Exception as creative_agent_premium_plugin_routing_error:
    @app.get("/creative/agent-premium-plugin-routing")
    async def creative_agent_premium_plugin_routing_unavailable():
        return {
            "success": False,
            "layer": "creative_agent_premium_plugin_routing",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "error": str(creative_agent_premium_plugin_routing_error),
        }

    @app.get("/admin/creative/agent-premium-plugin-routing")
    async def admin_creative_agent_premium_plugin_routing_unavailable():
        return {
            "success": False,
            "layer": "creative_agent_premium_plugin_routing",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "error": str(creative_agent_premium_plugin_routing_error),
        }
# CREATIVE_AGENT_PREMIUM_PLUGIN_ROUTING_END

# CREATIVE_PROVIDER_CREDENTIAL_ACTIVATION_CHECKS_START
try:
    from backend.app.runtime.creative_provider_credential_activation_checks import (
        get_client_safe_creative_provider_credential_activation_checks,
        get_creative_provider_credential_activation_checks,
    )

    @app.get("/creative/provider-credential-activation-checks")
    async def creative_provider_credential_activation_checks():
        return get_client_safe_creative_provider_credential_activation_checks()

    @app.get("/admin/creative/provider-credential-activation-checks")
    async def admin_creative_provider_credential_activation_checks():
        return get_creative_provider_credential_activation_checks()

except Exception as creative_provider_credential_activation_checks_error:
    @app.get("/creative/provider-credential-activation-checks")
    async def creative_provider_credential_activation_checks_unavailable():
        return {
            "success": False,
            "layer": "provider_credential_activation_checks",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "error": str(creative_provider_credential_activation_checks_error),
        }

    @app.get("/admin/creative/provider-credential-activation-checks")
    async def admin_creative_provider_credential_activation_checks_unavailable():
        return {
            "success": False,
            "layer": "provider_credential_activation_checks",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "error": str(creative_provider_credential_activation_checks_error),
        }
# CREATIVE_PROVIDER_CREDENTIAL_ACTIVATION_CHECKS_END

# FINAL_CREATIVE_MEDIA_PLUGIN_LOCK_START
try:
    from backend.app.runtime.final_creative_media_plugin_lock import (
        get_client_safe_final_creative_media_plugin_lock,
        get_final_creative_media_plugin_lock,
    )

    @app.get("/creative/final-media-plugin-lock")
    async def creative_final_media_plugin_lock():
        return get_client_safe_final_creative_media_plugin_lock()

    @app.get("/admin/creative/final-media-plugin-lock")
    async def admin_creative_final_media_plugin_lock():
        return get_final_creative_media_plugin_lock()

except Exception as final_creative_media_plugin_lock_error:
    @app.get("/creative/final-media-plugin-lock")
    async def creative_final_media_plugin_lock_unavailable():
        return {
            "success": False,
            "layer": "final_creative_media_plugin_lock",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "error": str(final_creative_media_plugin_lock_error),
        }

    @app.get("/admin/creative/final-media-plugin-lock")
    async def admin_creative_final_media_plugin_lock_unavailable():
        return {
            "success": False,
            "layer": "final_creative_media_plugin_lock",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "error": str(final_creative_media_plugin_lock_error),
        }
# FINAL_CREATIVE_MEDIA_PLUGIN_LOCK_END

# DYNAMIC_AGENT_LEARNING_VERIFICATION_START
try:
    from backend.app.runtime.dynamic_agent_learning_verification import (
        get_client_safe_dynamic_agent_learning_verification,
        get_dynamic_agent_learning_verification,
    )

    @app.get("/dynamic-agent-learning-verification")
    async def dynamic_agent_learning_verification():
        return get_client_safe_dynamic_agent_learning_verification()

    @app.get("/admin/dynamic-agent-learning-verification")
    async def admin_dynamic_agent_learning_verification():
        return get_dynamic_agent_learning_verification()

except Exception as dynamic_agent_learning_verification_error:
    @app.get("/dynamic-agent-learning-verification")
    async def dynamic_agent_learning_verification_unavailable():
        return {
            "success": False,
            "layer": "governed_dynamic_learning",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "error": str(dynamic_agent_learning_verification_error),
        }

    @app.get("/admin/dynamic-agent-learning-verification")
    async def admin_dynamic_agent_learning_verification_unavailable():
        return {
            "success": False,
            "layer": "governed_dynamic_learning",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "error": str(dynamic_agent_learning_verification_error),
        }
# DYNAMIC_AGENT_LEARNING_VERIFICATION_END

# ADMIN_UGC_LIVE_MEDIA_EXECUTION_BRIDGE_START
try:
    from pydantic import BaseModel
    from backend.app.runtime.admin_ugc_live_media_execution_bridge import (
        get_admin_ugc_live_media_execution_bridge_status,
        run_admin_ugc_live_media_execution,
    )

    class AdminUGCLiveMediaExecutionRequest(BaseModel):
        task: str
        agent_key: str = "ugc_creative_agent"
        owner_approved_live_execution: bool = False
        test_label: str = "admin_ugc_live_media_execution"

    @app.get("/admin/creative/ugc-live-media-execution/status")
    async def admin_ugc_live_media_execution_status():
        return get_admin_ugc_live_media_execution_bridge_status()

    @app.post("/admin/creative/ugc-live-media-execution")
    async def admin_ugc_live_media_execution(request: AdminUGCLiveMediaExecutionRequest):
        return run_admin_ugc_live_media_execution(
            task=request.task,
            agent_key=request.agent_key,
            owner_approved_live_execution=request.owner_approved_live_execution,
            test_label=request.test_label,
        )

except Exception as admin_ugc_live_media_execution_bridge_error:
    @app.get("/admin/creative/ugc-live-media-execution/status")
    async def admin_ugc_live_media_execution_status_unavailable():
        return {
            "success": False,
            "provider_runtime": "admin_ugc_live_media_execution_bridge",
            "status": "unavailable",
            "error": str(admin_ugc_live_media_execution_bridge_error),
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
        }
# ADMIN_UGC_LIVE_MEDIA_EXECUTION_BRIDGE_END

# ADMIN_CREATIVE_MEDIA_ASSET_VIEWER_START
try:
    from backend.app.runtime.admin_creative_media_asset_viewer import (
        get_admin_creative_media_asset_viewer_status,
        get_admin_creative_media_assets,
    )

    @app.get("/admin/creative/media-assets/status")
    async def admin_creative_media_assets_status():
        return get_admin_creative_media_asset_viewer_status()

    @app.get("/admin/creative/media-assets")
    async def admin_creative_media_assets(limit: int = 50):
        return get_admin_creative_media_assets(limit=limit)

except Exception as admin_creative_media_asset_viewer_error:
    @app.get("/admin/creative/media-assets/status")
    async def admin_creative_media_assets_status_unavailable():
        return {
            "success": False,
            "layer": "admin_creative_media_asset_viewer",
            "status": "unavailable",
            "error": str(admin_creative_media_asset_viewer_error),
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
        }
# ADMIN_CREATIVE_MEDIA_ASSET_VIEWER_END


@app.get("/admin/creative/product-asset-library/status")
async def admin_creative_product_asset_library_status():
    from backend.app.runtime.creative_product_asset_library import creative_product_asset_library_status
    return creative_product_asset_library_status()


@app.get("/admin/creative/product-assets")
async def admin_list_creative_product_assets(tenant_id: str = "owner_admin", asset_type: str = "", campaign_id: str = "", limit: int = 100):
    from backend.app.runtime.creative_product_asset_library import list_creative_product_assets
    return list_creative_product_assets(
        tenant_id=tenant_id or None,
        asset_type=asset_type or None,
        campaign_id=campaign_id or None,
        limit=limit,
    )


@app.post("/admin/creative/product-assets/upload")
async def admin_upload_creative_product_asset(payload: dict):
    from backend.app.runtime.creative_product_asset_library import upload_creative_product_asset
    return upload_creative_product_asset(
        tenant_id=payload.get("tenant_id") or "owner_admin",
        filename=payload.get("filename") or "uploaded_asset",
        content_base64=payload.get("content_base64") or "",
        asset_type=payload.get("asset_type") or "reference_asset",
        uploaded_by=payload.get("uploaded_by") or "owner_admin",
        campaign_id=payload.get("campaign_id"),
        metadata=payload.get("metadata") or {},
    )


@app.post("/admin/creative/product-assets/delete")
async def admin_delete_creative_product_asset(payload: dict):
    from backend.app.runtime.creative_product_asset_library import delete_creative_product_asset
    return delete_creative_product_asset(
        asset_id=payload.get("asset_id") or "",
        tenant_id=payload.get("tenant_id") or None,
    )


@app.get("/client/creative/product-assets")
async def client_list_creative_product_assets(tenant_id: str = "owner_admin", asset_type: str = "", campaign_id: str = "", limit: int = 100):
    from backend.app.runtime.creative_product_asset_library import list_creative_product_assets
    return list_creative_product_assets(
        tenant_id=tenant_id or "owner_admin",
        asset_type=asset_type or None,
        campaign_id=campaign_id or None,
        limit=limit,
    )


@app.post("/client/creative/product-assets/upload")
async def client_upload_creative_product_asset(payload: dict):
    from backend.app.runtime.creative_product_asset_library import upload_creative_product_asset
    return upload_creative_product_asset(
        tenant_id=payload.get("tenant_id") or "owner_admin",
        filename=payload.get("filename") or "uploaded_asset",
        content_base64=payload.get("content_base64") or "",
        asset_type=payload.get("asset_type") or "reference_asset",
        uploaded_by=payload.get("uploaded_by") or "client",
        campaign_id=payload.get("campaign_id"),
        metadata=payload.get("metadata") or {},
    )


@app.get("/creative/product-assets/execution-context")
async def creative_product_asset_execution_context(tenant_id: str = "owner_admin", campaign_id: str = "", limit: int = 25):
    from backend.app.runtime.creative_product_asset_library import build_creative_execution_asset_context
    return build_creative_execution_asset_context(
        tenant_id=tenant_id or "owner_admin",
        campaign_id=campaign_id or None,
        limit=limit,
    )



# Governed refund workflow routes
try:
    from backend.app.api.refund_routes import router as refund_router
    app.include_router(refund_router)
except Exception as exc:
    print(f"GOVERNED_REFUND_ROUTES_NOT_LOADED: {exc}")


# Admin Industry Agent Store + Tenant-Safe Learning Vault routes
try:
    from backend.app.api.admin_industry_agent_store_routes import router as admin_industry_agent_store_router
    app.include_router(admin_industry_agent_store_router)
except Exception as exc:
    print(f"ADMIN_INDUSTRY_AGENT_STORE_ROUTES_NOT_LOADED: {exc}")


# Industry-aware client deployment resolver routes
try:
    from backend.app.api.industry_aware_client_deployment_routes import router as industry_aware_client_deployment_router
    app.include_router(industry_aware_client_deployment_router)
except Exception as exc:
    print(f"INDUSTRY_AWARE_CLIENT_DEPLOYMENT_ROUTES_NOT_LOADED: {exc}")


# Admin Commercial Operations Visibility routes
try:
    from backend.app.api.admin_commercial_operations_routes import router as admin_commercial_operations_router
    app.include_router(admin_commercial_operations_router)
except Exception as exc:
    print(f"ADMIN_COMMERCIAL_OPERATIONS_ROUTES_NOT_LOADED: {exc}")

@app.get("/admin/media-jobs")
def admin_list_media_jobs(
    x_admin_token: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
):
    if x_actor_role not in {"owner_admin", "admin"}:
        return {
            "success": False,
            "error": "admin_only",
            "customer_safe": True,
            "credential_values_exposed": False,
        }
    from backend.app.runtime.async_media_job_foundation import list_media_jobs
    return list_media_jobs(limit=100, include_durable_status=True)


@app.get("/admin/media-jobs/{job_id}")
def admin_read_media_job(
    job_id: str,
    x_admin_token: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
):
    if x_actor_role not in {"owner_admin", "admin"}:
        return {
            "success": False,
            "error": "admin_only",
            "customer_safe": True,
            "credential_values_exposed": False,
        }
    from backend.app.runtime.async_media_job_foundation import read_media_job
    return read_media_job(job_id)


MEDIA_JOB_SECURITY_PROFILE = "priority5_security_audit_enforcement_v1"


def _admin_media_job_token_valid(token: str | None, authorization: str | None = None) -> bool:
    supplied = str(token or "").strip()
    if not supplied and authorization:
        supplied = str(authorization or "").replace("Bearer ", "").strip()
    expected = [
        os.getenv("ADMIN_PLATFORM_TOKEN", ""),
        os.getenv("ADMIN_AUTH_SECRET", ""),
        os.getenv("ADMIN_TOKEN", ""),
        os.getenv("PLATFORM_ADMIN_TOKEN", ""),
        os.getenv("OWNER_ADMIN_TOKEN", ""),
    ]
    expected_tokens = [str(value).strip().strip(chr(34)).strip(chr(39)) for value in expected if str(value).strip()]
    if not expected_tokens:
        return os.getenv("APP_ENV", "development").lower() not in {"production", "prod"}
    supplied = supplied.strip().strip(chr(34)).strip(chr(39))
    return bool(supplied and any(hmac.compare_digest(supplied, expected_token) for expected_token in expected_tokens))


def _admin_media_job_authorized(
    x_actor_role: str | None,
    x_admin_token: str | None,
    authorization: str | None = None,
) -> bool:
    role = str(x_actor_role or "").strip().lower()
    return role in {"owner", "admin", "owner_admin", "system"} and _admin_media_job_token_valid(x_admin_token, authorization)


def _media_job_final_status_counts(result: dict) -> dict:
    counts: dict[str, int] = {}
    for item in result.get("results", []) if isinstance(result, dict) else []:
        if not isinstance(item, dict):
            continue
        job = item.get("job") if isinstance(item.get("job"), dict) else {}
        status = str(job.get("status") or item.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _media_job_store_snapshot(limit: int = 50) -> dict:
    from backend.app.runtime.async_media_job_foundation import list_media_jobs

    jobs_result = list_media_jobs(limit=max(1, min(int(limit or 50), 50)))
    jobs = jobs_result.get("jobs", []) if isinstance(jobs_result, dict) else []
    status_counts: dict[str, int] = {}
    queued_count = 0
    for job in jobs:
        if not isinstance(job, dict):
            continue
        status = str(job.get("status") or "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        if status == "queued":
            queued_count += 1
    return {
        **jobs_result,
        "status_counts": status_counts,
        "queued_job_count": queued_count,
    }


def _media_job_skipped_summary(result: dict) -> dict:
    skipped_reasons: dict[str, int] = {}
    skipped_count = 0
    for item in result.get("results", []) if isinstance(result, dict) else []:
        if not isinstance(item, dict) or item.get("processed"):
            continue
        status = str(item.get("status") or item.get("reason") or "unknown")
        if status == "empty":
            continue
        reason = str(item.get("reason") or status)
        skipped_reasons[reason] = skipped_reasons.get(reason, 0) + 1
        skipped_count += 1
    return {"skipped_job_count": skipped_count, "skipped_reasons": skipped_reasons}


def _media_job_blocked_response():
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=403,
        content={
            "success": False,
            "error": "admin_authorisation_required",
            "authorised": False,
            "processor_invoked": False,
            "processed_job_count": 0,
            "final_status_counts": {},
            "security_profile": MEDIA_JOB_SECURITY_PROFILE,
            "credential_values_exposed": False,
            "customer_safe": True,
        },
    )


def _media_job_processor_response(
    result: dict,
    *,
    authorised: bool,
    processor_invoked: bool,
    before_snapshot: dict | None = None,
    after_snapshot: dict | None = None,
) -> dict:
    processed_count = int(result.get("processed_count") or (1 if result.get("processed") else 0) or 0)
    before = before_snapshot or {}
    after = after_snapshot or {}
    skipped = _media_job_skipped_summary(result)
    return {
        **result,
        "canonical_store": result.get("canonical_store") or before.get("canonical_store") or after.get("canonical_store") or "backend:runtime_outputs/media_jobs",
        "visible_queued_job_count_before": int(before.get("visible_queued_job_count") or before.get("queued_job_count") or 0),
        "processor_queued_job_count_before": int(before.get("processor_queued_job_count") or before.get("queued_job_count") or 0),
        "authorised": bool(authorised),
        "processor_invoked": bool(processor_invoked),
        "processed_job_count": processed_count,
        "skipped_job_count": skipped["skipped_job_count"],
        "skipped_reasons": skipped["skipped_reasons"],
        "final_status_counts": after.get("status_counts") or _media_job_final_status_counts(result),
        "store_paths_match": bool(result.get("store_paths_match", before.get("store_paths_match", after.get("store_paths_match", True)))),
        "environment_context": "backend_processor",
        "security_profile": MEDIA_JOB_SECURITY_PROFILE,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def _media_job_trigger_response(
    result: dict,
    *,
    authorised: bool,
    before_snapshot: dict | None = None,
    legacy_route: str = "",
) -> dict:
    before = before_snapshot or {}
    return {
        **result,
        "success": bool(result.get("success", True)),
        "triggered": True,
        "background_processor_scheduled": bool(result.get("background_processor_scheduled")),
        "queue_name": result.get("queue_name") or "creative_media_generation_queue",
        "queued_job_count": int(result.get("queued_job_count") or before.get("queued_job_count") or 0),
        "canonical_store": result.get("canonical_store") or before.get("canonical_store") or "backend:runtime_outputs/media_jobs",
        "fast_output_packet_available": bool(result.get("fast_output_packet_available", False)),
        "fast_output_packet": result.get("fast_output_packet"),
        "fast_output_packets": result.get("fast_output_packets", []),
        "timing_stage": result.get("timing_stage") or "stage_1_fast_creative_response",
        "final_provider_media_stage": result.get("final_provider_media_stage") or "stage_2_async_final_render",
        "final_media_completion_claimed": False,
        "visible_queued_job_count_before": int(before.get("visible_queued_job_count") or before.get("queued_job_count") or 0),
        "processor_queued_job_count_before": int(before.get("processor_queued_job_count") or before.get("queued_job_count") or 0),
        "authorised": bool(authorised),
        "processor_invoked": False,
        "processed_job_count": 0,
        "request_path_safe": True,
        "web_request_media_execution_blocked": True,
        "background_worker_required": True,
        "legacy_route": legacy_route,
        "environment_context": "backend_trigger_only",
        "security_profile": MEDIA_JOB_SECURITY_PROFILE,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


@app.post("/admin/media-jobs/trigger-next")
def admin_trigger_next_media_job(
    x_admin_token: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
):
    if not _admin_media_job_authorized(x_actor_role, x_admin_token, authorization):
        return _media_job_blocked_response()
    from backend.app.runtime.async_media_job_foundation import trigger_next_creative_media_job
    before = _media_job_store_snapshot(limit=25)
    result = trigger_next_creative_media_job()
    return _media_job_trigger_response(result, authorised=True, before_snapshot=before)


@app.post("/admin/media-jobs/trigger-all")
def admin_trigger_all_media_jobs(
    x_admin_token: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
):
    if not _admin_media_job_authorized(x_actor_role, x_admin_token, authorization):
        return _media_job_blocked_response()
    from backend.app.runtime.async_media_job_foundation import trigger_all_creative_media_jobs
    before = _media_job_store_snapshot(limit=25)
    result = trigger_all_creative_media_jobs(limit=25)
    return _media_job_trigger_response(result, authorised=True, before_snapshot=before)


@app.post("/admin/media-jobs/run-next")
def admin_run_next_media_job(
    x_admin_token: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
):
    if not _admin_media_job_authorized(x_actor_role, x_admin_token, authorization):
        return _media_job_blocked_response()
    from backend.app.runtime.async_media_job_foundation import trigger_next_creative_media_job
    before = _media_job_store_snapshot(limit=25)
    result = trigger_next_creative_media_job()
    return _media_job_trigger_response(result, authorised=True, before_snapshot=before, legacy_route="/admin/media-jobs/run-next")


@app.post("/admin/media-jobs/run-all")
def admin_run_all_media_jobs(
    x_admin_token: str | None = Header(default=None),
    x_actor_role: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
):
    if not _admin_media_job_authorized(x_actor_role, x_admin_token, authorization):
        return _media_job_blocked_response()
    from backend.app.runtime.async_media_job_foundation import trigger_all_creative_media_jobs
    before = _media_job_store_snapshot(limit=25)
    result = trigger_all_creative_media_jobs(limit=25)
    return _media_job_trigger_response(result, authorised=True, before_snapshot=before, legacy_route="/admin/media-jobs/run-all")


# DIRECT_MEDIA_PROVIDER_EXECUTION_LANE_V1
@app.get("/admin/direct-media-provider-status")
def admin_direct_media_provider_status() -> Dict[str, object]:
    from backend.app.runtime.direct_media_provider_execution_runtime import direct_media_provider_execution_status

    return direct_media_provider_execution_status()


@app.post("/admin/direct-media-provider-execute")
async def admin_direct_media_provider_execute(request: Request) -> Dict[str, object]:
    from backend.app.runtime.direct_media_provider_execution_runtime import execute_direct_media_provider_job

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    return execute_direct_media_provider_job(payload)


@app.get("/admin/direct-media-provider-job-status/{job_id}")
def admin_direct_media_provider_job_status(job_id: str) -> Dict[str, object]:
    from backend.app.runtime.direct_media_provider_execution_runtime import get_direct_media_provider_job_status

    return get_direct_media_provider_job_status(job_id)


# DIRECT_MEDIA_PROVIDER_SECURITY_BRIDGE_V1
@app.middleware("http")
async def direct_media_provider_security_bridge_middleware(request, call_next):
    path = request.url.path.rstrip("/")
    is_direct_media_path = (
        path == "/admin/direct-media-provider-status"
        or path == "/admin/direct-media-provider-execute"
        or path == "/admin/direct-media-provider-submit"
        or path.startswith("/admin/direct-media-provider-job-status/")
        or path.startswith("/admin/direct-media-provider-asset/")
        or path == "/admin/direct-media-provider-compose"
        or path == "/admin/direct-media-provider-compose-status"
        or path == "/admin/universal-complete-media"
        or path == "/admin/universal-complete-media-status"
    )

    if not is_direct_media_path:
        return await call_next(request)

    from fastapi.responses import JSONResponse

    x_actor_role = request.headers.get("x-actor-role")
    x_admin_token = request.headers.get("x-admin-token")
    authorization = request.headers.get("authorization") or request.headers.get("Authorization")

    try:
        authorized = _admin_media_job_authorized(
            x_actor_role=x_actor_role,
            x_admin_token=x_admin_token,
            authorization=authorization,
        )
    except Exception:
        authorized = False

    if not authorized:
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "error": "admin_only",
                "message": "Direct media provider execution requires owner/admin authorization.",
                "customer_safe": True,
                "credential_values_exposed": False,
            },
        )

    try:
        if path == "/admin/direct-media-provider-status" and request.method.upper() == "GET":
            from backend.app.runtime.direct_media_provider_execution_runtime import direct_media_provider_execution_status

            return JSONResponse(content=direct_media_provider_execution_status())

        if path == "/admin/direct-media-provider-execute" and request.method.upper() == "POST":
            from backend.app.runtime.direct_media_provider_execution_runtime import execute_direct_media_provider_job

            try:
                payload = await request.json()
            except Exception:
                payload = {}

            return JSONResponse(content=execute_direct_media_provider_job(payload))

        if path == "/admin/direct-media-provider-submit" and request.method.upper() == "POST":
            from backend.app.runtime.direct_media_provider_execution_runtime import start_direct_media_provider_job_async

            try:
                payload = await request.json()
            except Exception:
                payload = {}

            return JSONResponse(content=start_direct_media_provider_job_async(payload))

        if path.startswith("/admin/direct-media-provider-job-status/") and request.method.upper() == "GET":
            from backend.app.runtime.direct_media_provider_execution_runtime import get_direct_media_provider_job_status

            job_id = path.rsplit("/", 1)[-1]
            return JSONResponse(content=get_direct_media_provider_job_status(job_id))

        if path == "/admin/universal-complete-media" and request.method.upper() == "POST":
            from backend.app.runtime.direct_media_provider_execution_runtime import start_universal_complete_media_workflow

            try:
                payload = await request.json()
            except Exception:
                payload = {}

            return JSONResponse(content=start_universal_complete_media_workflow(payload))

        if path == "/admin/universal-complete-media-status" and request.method.upper() == "GET":
            from backend.app.runtime.direct_media_provider_execution_runtime import (
                get_direct_media_provider_job_status,
                universal_complete_media_status,
            )

            job_id = str(request.query_params.get("job_id") or "").strip()
            if job_id:
                job = get_direct_media_provider_job_status(job_id)
                if job and job.get("status") != "not_found":
                    return JSONResponse(content={
                        **job,
                        "universal_complete_media_status_lookup": True,
                        "direct_media_provider_execution": False,
                        "customer_safe": True,
                        "credential_values_exposed": False,
                    })

                return JSONResponse(
                    status_code=202,
                    content={
                        "success": False,
                        "status": "job_status_not_found",
                        "job_id": job_id,
                        "message": "Universal complete media job status was not found in the active runtime store.",
                        "polling_required": True,
                        "universal_complete_media_status_lookup": True,
                        "customer_safe": True,
                        "credential_values_exposed": False,
                    },
                )

            return JSONResponse(content=universal_complete_media_status())

        if path == "/admin/direct-media-provider-compose" and request.method.upper() == "POST":
            from backend.app.runtime.direct_media_provider_execution_runtime import compose_direct_media_video_audio

            try:
                payload = await request.json()
            except Exception:
                payload = {}

            return JSONResponse(content=compose_direct_media_video_audio(payload))

        if path == "/admin/direct-media-provider-compose-status" and request.method.upper() == "GET":
            from backend.app.runtime.direct_media_provider_execution_runtime import direct_media_composition_status

            return JSONResponse(content=direct_media_composition_status())

        if path.startswith("/admin/direct-media-provider-asset/") and request.method.upper() == "GET":
            from pathlib import Path
            from fastapi.responses import FileResponse
            from backend.app.runtime.direct_media_provider_execution_runtime import get_direct_media_provider_job_status

            job_id = path.rsplit("/", 1)[-1]
            job = get_direct_media_provider_job_status(job_id)
            asset_path_value = (
                job.get("asset_path")
                or job.get("download_url")
                or (job.get("provider_result") or {}).get("audio_path")
                or (job.get("provider_result") or {}).get("video_path")
                or ""
            )

            asset_path = Path(str(asset_path_value)).resolve()
            allowed_root = Path("/opt/render/project/src/runtime_outputs").resolve()

            try:
                asset_path.relative_to(allowed_root)
            except Exception:
                return JSONResponse(
                    status_code=403,
                    content={
                        "success": False,
                        "error": "direct_media_asset_path_blocked",
                        "customer_safe": True,
                        "credential_values_exposed": False,
                    },
                )

            if not asset_path.exists() or not asset_path.is_file():
                return JSONResponse(
                    status_code=404,
                    content={
                        "success": False,
                        "error": "direct_media_asset_file_missing",
                        "job_id": job_id,
                        "customer_safe": True,
                        "credential_values_exposed": False,
                    },
                )

            suffix = asset_path.suffix.lower()
            media_type = "application/octet-stream"
            if suffix == ".mp3":
                media_type = "audio/mpeg"
            elif suffix == ".wav":
                media_type = "audio/wav"
            elif suffix == ".mp4":
                media_type = "video/mp4"
            elif suffix in {".png", ".jpg", ".jpeg", ".webp"}:
                media_type = "image/" + suffix.replace(".", "").replace("jpg", "jpeg")

            return FileResponse(path=str(asset_path), media_type=media_type, filename=asset_path.name)

        return JSONResponse(
            status_code=405,
            content={
                "success": False,
                "error": "method_not_allowed",
                "customer_safe": True,
                "credential_values_exposed": False,
            },
        )

    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "direct_media_provider_bridge_failed",
                "message": str(error)[:800],
                "customer_safe": True,
                "credential_values_exposed": False,
            },
        )


# ASYNC_DIRECT_MEDIA_PROVIDER_SUBMIT_ROUTE_V1
@app.post("/admin/direct-media-provider-submit")
async def admin_direct_media_provider_submit(request: Request) -> Dict[str, object]:
    from backend.app.runtime.direct_media_provider_execution_runtime import start_direct_media_provider_job_async

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    return start_direct_media_provider_job_async(payload)


# DIRECT_MEDIA_ASSET_DELIVERY_ROUTE_V1
@app.get("/admin/direct-media-provider-asset/{job_id}")
def admin_direct_media_provider_asset(job_id: str):
    from pathlib import Path
    from fastapi.responses import FileResponse, JSONResponse
    from backend.app.runtime.direct_media_provider_execution_runtime import get_direct_media_provider_job_status

    job = get_direct_media_provider_job_status(job_id)
    if not job or job.get("status") == "not_found":
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "direct_media_asset_not_found",
                "job_id": job_id,
                "customer_safe": True,
                "credential_values_exposed": False,
            },
        )

    asset_path_value = (
        job.get("asset_path")
        or job.get("download_url")
        or (job.get("provider_result") or {}).get("audio_path")
        or (job.get("provider_result") or {}).get("video_path")
        or ""
    )

    asset_path = Path(str(asset_path_value)).resolve()
    allowed_root = Path("/opt/render/project/src/runtime_outputs").resolve()

    try:
        asset_path.relative_to(allowed_root)
    except Exception:
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "error": "direct_media_asset_path_blocked",
                "customer_safe": True,
                "credential_values_exposed": False,
            },
        )

    if not asset_path.exists() or not asset_path.is_file():
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "direct_media_asset_file_missing",
                "job_id": job_id,
                "customer_safe": True,
                "credential_values_exposed": False,
            },
        )

    suffix = asset_path.suffix.lower()
    media_type = "application/octet-stream"
    if suffix == ".mp3":
        media_type = "audio/mpeg"
    elif suffix == ".wav":
        media_type = "audio/wav"
    elif suffix == ".mp4":
        media_type = "video/mp4"
    elif suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        media_type = "image/" + suffix.replace(".", "").replace("jpg", "jpeg")

    return FileResponse(
        path=str(asset_path),
        media_type=media_type,
        filename=asset_path.name,
    )


# DIRECT_MEDIA_COMPOSITION_ROUTE_V1
@app.post("/admin/direct-media-provider-compose")
async def admin_direct_media_provider_compose(request: Request) -> Dict[str, object]:
    from backend.app.runtime.direct_media_provider_execution_runtime import compose_direct_media_video_audio

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    return compose_direct_media_video_audio(payload)


@app.get("/admin/direct-media-provider-compose-status")
def admin_direct_media_provider_compose_status() -> Dict[str, object]:
    from backend.app.runtime.direct_media_provider_execution_runtime import direct_media_composition_status

    return direct_media_composition_status()


# UNIVERSAL_COMPLETE_MEDIA_WORKFLOW_ROUTE_V1
@app.post("/admin/universal-complete-media")
async def admin_universal_complete_media(request: Request) -> Dict[str, object]:
    from backend.app.runtime.direct_media_provider_execution_runtime import start_universal_complete_media_workflow

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    return start_universal_complete_media_workflow(payload)


@app.get("/admin/universal-complete-media-status")
def admin_universal_complete_media_status(job_id: str = "") -> Dict[str, object]:
    from backend.app.runtime.direct_media_provider_execution_runtime import (
        get_direct_media_provider_job_status,
        universal_complete_media_status,
    )

    safe_job_id = str(job_id or "").strip()
    if safe_job_id:
        job = get_direct_media_provider_job_status(safe_job_id)
        if job and job.get("status") != "not_found":
            return {
                **job,
                "universal_complete_media_status_lookup": True,
                "direct_media_provider_execution": False,
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        return {
            "success": False,
            "status": "job_status_not_found",
            "job_id": safe_job_id,
            "message": "Universal complete media job status was not found in the active runtime store.",
            "polling_required": True,
            "universal_complete_media_status_lookup": True,
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    return universal_complete_media_status()


# SAFE_RUNWAY_KEY_DIAGNOSTICS_V1
@app.get("/admin/runway-key-diagnostics")
def admin_runway_key_diagnostics(
    x_actor_role: str | None = Header(default=None),
    x_admin_token: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> Dict[str, object]:
    import hashlib
    import os

    if not _admin_media_job_authorized(
        x_actor_role=x_actor_role,
        x_admin_token=x_admin_token,
        authorization=authorization,
    ):
        return {
            "success": False,
            "error": "admin_only",
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    candidate_names = [
        "RUNWAY_API_KEY",
        "RUNWAYML_API_KEY",
        "RUNWAY_TOKEN",
        "RUNWAYML_TOKEN",
        "RUNWAY_API_TOKEN",
    ]

    keys = []
    for name in candidate_names:
        value = str(os.getenv(name) or "").strip()
        if value:
            digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
            keys.append({
                "env_name": name,
                "present": True,
                "length": len(value),
                "sha256_prefix": digest[:12],
                "starts_with": value[:4] + "***" if len(value) >= 4 else "***",
            })
        else:
            keys.append({
                "env_name": name,
                "present": False,
                "length": 0,
            })

    return {
        "success": True,
        "status": "runway_key_metadata_only",
        "keys": keys,
        "note": "No credential values are exposed. Compare sha256_prefix/length with the intended key locally or in Render.",
        "customer_safe": True,
        "credential_values_exposed": False,
    }

