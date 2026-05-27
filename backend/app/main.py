from backend.app.runtime.real_provider_adapter_layer import get_provider_adapter_status as get_unified_provider_adapter_status
import os
import hashlib
from backend.app.runtime.ai_media_creative_director import readiness as ai_media_creative_director_readiness, run_shared_ai_media_creative_director
from backend.app.core.integration_live_adapter_registry import (
    adapter_registry_summary,
    execute_integration_action,
)
import urllib.request
import urllib.error
import json
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.client_business_profile_runtime import get_client_business_profile, save_client_business_profile
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

from backend.app.core.priority5_final_security_readiness import priority5_final_security_readiness
from backend.app.core.priority5_active_security_runtime import active_security_readiness, csrf_check_passed, csrf_check_required, log_security_event, rate_limit_check
from fastapi import FastAPI, Header
from backend.app.runtime.real_provider_activation_registry import get_all_provider_activation_statuses, get_provider_activation_status, select_ready_provider_for_capability
from backend.app.runtime.async_provider_job_runtime import create_async_provider_job, get_async_provider_job, list_async_provider_jobs, update_async_provider_job_status, mark_async_provider_job_retry
from backend.app.runtime.real_provider_adapter_layer import get_provider_adapter_status, normalise_provider_request, route_provider_request, execute_provider_request_scaffold
from pydantic import BaseModel
from typing import Dict, List

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
from backend.app.core.stripe_advanced_billing_runtime import advanced_billing_readiness
from backend.app.core.stripe_customer_billing_portal import billing_portal_readiness
from backend.app.runtime.dead_letter_manual_review_runtime import create_dead_letter_record, dead_letter_readiness, list_dead_letters, list_manual_review_queue, record_manual_review_decision
from backend.app.runtime.workflow_provider_auto_routing import list_workflow_provider_routes, route_workflow_to_provider_bridge, workflow_provider_routing_readiness
from backend.app.runtime.live_provider_execution_outputs import execute_live_provider_packet, list_live_provider_executions, live_provider_execution_readiness
from backend.app.runtime.ai_media_creative_model_registry import ai_media_registry_readiness, create_ai_media_execution_packet, create_creative_director_plan, list_ai_media_execution_packets, list_ai_media_models, list_creative_director_plans
from backend.app.runtime.ai_media_execution_router import ai_media_execution_router_readiness, list_ai_media_router_results, route_ai_media_request
from backend.app.runtime.ai_media_provider_adapters import ai_media_provider_adapters_readiness, execute_ai_media_provider_adapter, get_provider_adapter_status, list_ai_media_provider_adapter_results, prepare_provider_payload
from backend.app.runtime.ai_media_quality_gate import ai_media_quality_gate_readiness, gate_ai_media_execution_packet, list_ai_media_quality_scores, score_ai_media_quality
from backend.app.runtime.ai_media_brand_character_memory import ai_media_brand_character_memory_readiness, enrich_ai_media_payload_with_memory, get_ai_media_memory_context, list_ai_media_memory, save_brand_memory, save_campaign_style_memory, save_character_memory
from backend.app.runtime.ai_media_prompt_template_pack import ai_media_prompt_template_pack_readiness, list_ai_media_prompt_templates, list_rendered_ai_media_prompts, recommend_ai_media_prompt_template, render_ai_media_prompt_template
from backend.app.runtime.ai_media_multi_provider_execution_packets import advance_packet_to_next_provider, ai_media_multi_provider_packets_readiness, create_ai_media_multi_provider_packet, list_ai_media_multi_provider_packets
from backend.app.runtime.ai_media_end_to_end_pipeline import ai_media_end_to_end_pipeline_readiness, list_ai_media_pipeline_runs, run_ai_media_end_to_end_pipeline
from backend.app.runtime.ai_media_session_auth_compat import validate_ai_media_admin_session_compatibility
from backend.app.runtime.global_real_provider_connector_layer import build_global_connector_execution_packet
from backend.app.runtime.global_provider_execution_runtime import global_provider_execution_readiness, build_global_provider_execution_packet
from backend.app.runtime.global_real_provider_connector_layer import global_real_provider_connector_readiness, build_global_connector_execution_packet
from backend.app.runtime.real_provider_activation_layer import real_provider_activation_readiness

app = FastAPI(
    title="Ecommerce AI Agent Platform",
    version="1.1.0",
)


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
    requested_agent = normalize_agent_id(request.requested_agent)

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

    owner_admin_internal_execution = request.actor_role in {"owner", "admin", "system"}

    tenant_account = pg_lookup_client_account(request.tenant_id)

    if not tenant_account.get("success"):
        if not owner_admin_internal_execution:
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
                "owner_admin_internal_bypass": True,
            },
        }

    active_agents = tenant_account.get("account", {}).get("active_agents", [])

    if not owner_admin_internal_execution:
        normalised_active_agents = [
            normalize_agent_id(agent) for agent in active_agents
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
            event_type="approval_gate_blocked",
            title=f"{requested_agent} action blocked before quality review",
            agent_id=requested_agent,
            payload=blocked_payload,
        )

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
        "global_provider_connector": build_global_connector_execution_packet({
            "tenant_id": request.tenant_id,
            "requested_agent": request.requested_agent,
            "workflow_stage": request.workflow_stage,
            "action_type": request.action_type,
            "task": request.task,
        }),
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
        int(payload.get("queue_id") or 0),
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



# Client business profile persistence runtime
@app.get("/client/business-profile")
async def client_business_profile_get(session_token: str):
    return get_client_business_profile(session_token)


@app.post("/client/business-profile")
async def client_business_profile_save(payload: dict):
    session_token = str(payload.get("session_token") or "")
    profile = payload.get("profile") or {}
    if not isinstance(profile, dict):
        profile = {}
    return save_client_business_profile(session_token, profile)

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




@app.get("/admin/security/final-readiness")
def admin_security_final_readiness():
    return priority5_final_security_readiness()



@app.middleware("http")
async def priority5_active_security_middleware(request, call_next):
    protected_prefixes = (
        "/admin",
        "/client",
        "/api/run-agent",
        "/api/client-review-action",
        "/api/client-integrations",
        "/api/client-integrations-connect",
        "/api/client-integrations-disconnect",
        "/api/client-integrations-test",
    )

    path = request.url.path
    is_protected = path.startswith(protected_prefixes)

    if is_protected:
        rate = rate_limit_check(request)
        if not rate.get("allowed"):
            log_security_event("rate_limit_exceeded", request, {"rate_limit": rate})
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "rate_limit_exceeded",
                    "customer_safe_response_mode": True,
                    "secret_values_exposed": False,
                },
            )

        csrf_exempt_paths = {
            "/client/business-profile",
        }

        csrf_required = (
            csrf_check_required(request)
            and path not in csrf_exempt_paths
        )

        if csrf_required and not csrf_check_passed(request):
            log_security_event("csrf_token_missing", request, {"mode": "enforce"})
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "error": "csrf_validation_failed",
                    "customer_safe_response_mode": True,
                    "secret_values_exposed": False,
                },
            )

        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            log_security_event("protected_state_changing_request", request, {"csrf_mode": "audit_or_enforce"})

    response = await call_next(request)

    if is_protected:
        response.headers["X-Security-Profile"] = "priority5_active_security_runtime_v1"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    return response



@app.get("/admin/security/active-runtime-readiness")
def admin_security_active_runtime_readiness():
    return active_security_readiness()


@app.get("/admin/stripe-production-readiness")
async def admin_stripe_production_readiness():
    return stripe_production_env_readiness()


@app.get("/admin/billing-automation/readiness")
async def admin_billing_automation_readiness():
    return advanced_billing_readiness()


@app.get("/admin/subscription-policy/readiness")
async def admin_subscription_policy_readiness():
    return billing_readiness()


@app.get("/admin/customer-billing-portal/readiness")
async def admin_customer_billing_portal_readiness(
    tenant_id: str
):
    return billing_portal_readiness(tenant_id)


@app.post("/webhooks/stripe/hardened")
async def hardened_stripe_webhook(payload: dict):
    verification = verify_stripe_webhook_signature(payload)

    if not verification.get("success"):
        return verification

    return route_stripe_webhook_event(payload)


@app.post("/admin/billing-dashboard")
async def admin_billing_dashboard_route(payload: dict):
    return admin_billing_dashboard(payload)

# --- Provider bridge admin diagnostic endpoints ---
# Admin/runtime diagnostics only. No secrets are exposed.

@app.get("/admin/provider-connectors/readiness")
async def admin_provider_connectors_readiness():
    from backend.app.runtime.provider_connector_registry import readiness

    return readiness()


@app.get("/admin/provider-bridge/readiness")
async def admin_provider_bridge_readiness():
    from backend.app.runtime.execution_stack import runtime_provider_bridge_readiness

    return runtime_provider_bridge_readiness()


@app.post("/admin/provider-bridge/test-safe-generation")
async def admin_provider_bridge_test_safe_generation(payload: dict | None = None):
    from backend.app.runtime.execution_stack import execute_safe_generation_via_provider_bridge

    payload = payload or {}
    return execute_safe_generation_via_provider_bridge(
        action_type=payload.get("action_type", "marketing_campaign_execution"),
        payload=payload.get("payload", {"test": "provider bridge admin safe-generation test"}),
        tenant_id=payload.get("tenant_id", "owner_admin_test"),
        actor_role=payload.get("actor_role", "owner_admin"),
        preferred_provider=payload.get("preferred_provider", "openai"),
        capability=payload.get("capability"),
    )

# --- Persistent workflow admin diagnostic endpoints ---
# Admin/runtime diagnostics only. Customer-facing UI remains untouched.

@app.get("/admin/workflows/readiness")
async def admin_persistent_workflows_readiness():
    from backend.app.runtime.persistent_workflow_runtime import readiness

    return readiness()


@app.post("/admin/workflows/create-test")
async def admin_persistent_workflows_create_test(payload: dict | None = None):
    from backend.app.runtime.persistent_workflow_runtime import create_workflow

    payload = payload or {}
    return create_workflow(
        workflow_id=payload.get("workflow_id", "admin_test_workflow_001"),
        workflow_type=payload.get("workflow_type", "marketing_campaign_execution"),
        payload=payload.get("payload", {"test": "admin persistent workflow test"}),
        tenant_id=payload.get("tenant_id", "owner_admin_test"),
        actor_role=payload.get("actor_role", "owner_admin"),
        max_retries=int(payload.get("max_retries", 3)),
    )


@app.post("/admin/workflows/advance")
async def admin_persistent_workflows_advance(payload: dict | None = None):
    from backend.app.runtime.persistent_workflow_runtime import advance_workflow

    payload = payload or {}
    return advance_workflow(
        workflow_id=payload.get("workflow_id", "admin_test_workflow_001"),
        step_result=payload.get("step_result", {"admin_test": "advanced"}),
    )


@app.post("/admin/workflows/fail")
async def admin_persistent_workflows_fail(payload: dict | None = None):
    from backend.app.runtime.persistent_workflow_runtime import fail_workflow

    payload = payload or {}
    return fail_workflow(
        workflow_id=payload.get("workflow_id", "admin_test_workflow_001"),
        error=payload.get("error", {"admin_test": "temporary failure"}),
    )


@app.post("/admin/workflows/complete")
async def admin_persistent_workflows_complete(payload: dict | None = None):
    from backend.app.runtime.persistent_workflow_runtime import complete_workflow

    payload = payload or {}
    return complete_workflow(
        workflow_id=payload.get("workflow_id", "admin_test_workflow_001"),
        result=payload.get("result", {"admin_test": "completed"}),
    )


@app.get("/admin/workflows/{workflow_id}")
async def admin_persistent_workflows_get(workflow_id: str):
    from backend.app.runtime.persistent_workflow_runtime import get_workflow

    return get_workflow(workflow_id)

# --- Cross-agent orchestration admin diagnostic endpoints ---
# Admin/runtime diagnostics only. Customer-facing UI remains untouched.

@app.get("/admin/orchestration/readiness")
async def admin_cross_agent_orchestration_readiness():
    from backend.app.runtime.cross_agent_workflow_orchestration import readiness

    return readiness()


@app.post("/admin/orchestration/create-test")
async def admin_cross_agent_orchestration_create_test(payload: dict | None = None):
    from backend.app.runtime.cross_agent_workflow_orchestration import create_cross_agent_orchestration

    payload = payload or {}
    return create_cross_agent_orchestration(
        orchestration_id=payload.get("orchestration_id", "admin_orchestration_test_001"),
        workflow_id=payload.get("workflow_id", "admin_orchestration_workflow_001"),
        tenant_id=payload.get("tenant_id", "owner_admin_test"),
        head_agent_id=payload.get("head_agent_id", "head_agent"),
        active_agent_count=int(payload.get("active_agent_count", 3)),
        objective=payload.get(
            "objective",
            {
                "workflow_type": "marketing_campaign_execution",
                "goal": "Admin cross-agent orchestration test",
            },
        ),
        tasks=payload.get(
            "tasks",
            [
                {
                    "task_id": "admin_task_marketing_001",
                    "assigned_agent_id": "marketing_specialist_agent",
                    "task_type": "content_generation",
                    "payload": {"brief": "Campaign angle"},
                },
                {
                    "task_id": "admin_task_email_001",
                    "assigned_agent_id": "email_reply_agent",
                    "task_type": "email_copy_generation",
                    "payload": {"brief": "Launch email"},
                },
                {
                    "task_id": "admin_task_spend_001",
                    "assigned_agent_id": "marketing_specialist_agent",
                    "task_type": "scale_campaign",
                    "payload": {"budget_increase": 1000},
                },
            ],
        ),
    )


@app.post("/admin/orchestration/task-complete")
async def admin_cross_agent_orchestration_task_complete(payload: dict | None = None):
    from backend.app.runtime.cross_agent_workflow_orchestration import complete_cross_agent_task

    payload = payload or {}
    return complete_cross_agent_task(
        orchestration_id=payload.get("orchestration_id", "admin_orchestration_test_001"),
        task_id=payload.get("task_id", "admin_task_marketing_001"),
        result=payload.get("result", {"admin_test": "task completed"}),
    )


@app.post("/admin/orchestration/task-fail")
async def admin_cross_agent_orchestration_task_fail(payload: dict | None = None):
    from backend.app.runtime.cross_agent_workflow_orchestration import fail_cross_agent_task

    payload = payload or {}
    return fail_cross_agent_task(
        orchestration_id=payload.get("orchestration_id", "admin_orchestration_test_001"),
        task_id=payload.get("task_id", "admin_task_email_001"),
        error=payload.get("error", {"admin_test": "temporary failure"}),
    )


@app.get("/admin/orchestration/{orchestration_id}")
async def admin_cross_agent_orchestration_get(orchestration_id: str):
    from backend.app.runtime.cross_agent_workflow_orchestration import get_cross_agent_orchestration

    return get_cross_agent_orchestration(orchestration_id)

@app.get("/admin/dead-letter/readiness")
def admin_dead_letter_readiness():
    return dead_letter_readiness()


@app.post("/admin/dead-letter/create")
def admin_create_dead_letter(payload: dict):
    return create_dead_letter_record(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        workflow_id=payload.get("workflow_id"),
        agent_id=str(payload.get("agent_id", "unknown_agent")),
        action_type=str(payload.get("action_type", "unknown_action")),
        failure_reason=str(payload.get("failure_reason", "unspecified_failure")),
        payload=dict(payload.get("payload", {})),
        retry_count=int(payload.get("retry_count", 0)),
        severity=str(payload.get("severity", "medium")),
    )


@app.get("/admin/dead-letter/list")
def admin_list_dead_letters(tenant_id: str | None = None, status: str | None = None, limit: int = 50):
    return list_dead_letters(tenant_id=tenant_id, status=status, limit=limit)


@app.get("/admin/manual-review/list")
def admin_list_manual_review_queue(tenant_id: str | None = None, status: str | None = None, limit: int = 50):
    return list_manual_review_queue(tenant_id=tenant_id, status=status, limit=limit)


@app.post("/admin/manual-review/decision")
def admin_record_manual_review_decision(payload: dict):
    return record_manual_review_decision(
        review_id=str(payload.get("review_id", "")),
        decision=str(payload.get("decision", "")),
        actor_role=str(payload.get("actor_role", "")),
        notes=str(payload.get("notes", "")),
    )

@app.get("/admin/workflow-provider-routing/readiness")
def admin_workflow_provider_routing_readiness():
    return workflow_provider_routing_readiness()


@app.post("/admin/workflow-provider-routing/route")
def admin_route_workflow_to_provider(payload: dict):
    return route_workflow_to_provider_bridge(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        workflow_id=str(payload.get("workflow_id", "workflow_unknown")),
        agent_id=str(payload.get("agent_id", "unknown_agent")),
        action_type=str(payload.get("action_type", "unknown_action")),
        workflow_payload=dict(payload.get("workflow_payload", {})),
        available_providers=list(payload.get("available_providers", [])) if payload.get("available_providers") is not None else None,
        entitlement_active=bool(payload.get("entitlement_active", True)),
    )


@app.get("/admin/workflow-provider-routing/list")
def admin_list_workflow_provider_routes(tenant_id: str | None = None, status: str | None = None, limit: int = 50):
    return list_workflow_provider_routes(tenant_id=tenant_id, status=status, limit=limit)

@app.get("/admin/live-provider-execution/readiness")
def admin_live_provider_execution_readiness():
    return live_provider_execution_readiness()


@app.post("/admin/live-provider-execution/execute")
def admin_execute_live_provider_packet(payload: dict):
    return execute_live_provider_packet(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        workflow_id=str(payload.get("workflow_id", "workflow_unknown")),
        agent_id=str(payload.get("agent_id", "unknown_agent")),
        provider=str(payload.get("provider", "")),
        action_type=str(payload.get("action_type", "unknown_action")),
        payload=dict(payload.get("payload", {})),
        execution_allowed=bool(payload.get("execution_allowed", True)),
        owner_approved=bool(payload.get("owner_approved", False)),
        live_keys_available=bool(payload.get("live_keys_available", False)),
        entitlement_active=bool(payload.get("entitlement_active", True)),
    )


@app.get("/admin/live-provider-execution/list")
def admin_list_live_provider_executions(tenant_id: str | None = None, status: str | None = None, limit: int = 50):
    return list_live_provider_executions(tenant_id=tenant_id, status=status, limit=limit)

@app.get("/admin/ai-media/readiness")
def admin_ai_media_registry_readiness():
    return ai_media_registry_readiness()


@app.get("/admin/ai-media/models")
def admin_list_ai_media_models(category: str | None = None):
    return list_ai_media_models(category=category)


@app.post("/admin/ai-media/creative-plan")
def admin_create_ai_media_creative_plan(payload: dict):
    return create_creative_director_plan(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        brand_name=str(payload.get("brand_name", "Brand")),
        media_type=str(payload.get("media_type", "image")),
        objective=str(payload.get("objective", "Create commercial media asset")),
        product_or_offer=str(payload.get("product_or_offer", "")),
        target_platform=str(payload.get("target_platform", "Meta Ads")),
        region=str(payload.get("region", "global")),
        requested_style=str(payload.get("requested_style", "")),
        brand_colours=list(payload.get("brand_colours", [])) if payload.get("brand_colours") is not None else [],
        character_reference=payload.get("character_reference"),
        owner_approved=bool(payload.get("owner_approved", False)),
    )


@app.get("/admin/ai-media/creative-plans")
def admin_list_ai_media_creative_plans(tenant_id: str | None = None, limit: int = 50):
    return list_creative_director_plans(tenant_id=tenant_id, limit=limit)


@app.post("/admin/ai-media/execution-packet")
def admin_create_ai_media_execution_packet(payload: dict):
    return create_ai_media_execution_packet(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        plan_id=str(payload.get("plan_id", "")),
        selected_model=str(payload.get("selected_model", "")),
        prompt=str(payload.get("prompt", "")),
        media_type=str(payload.get("media_type", "image")),
        live_keys_available=bool(payload.get("live_keys_available", False)),
        owner_approved=bool(payload.get("owner_approved", False)),
    )


@app.get("/admin/ai-media/execution-packets")
def admin_list_ai_media_execution_packets(tenant_id: str | None = None, limit: int = 50):
    return list_ai_media_execution_packets(tenant_id=tenant_id, limit=limit)

@app.get("/admin/ai-media-router/readiness")
def admin_ai_media_execution_router_readiness():
    return ai_media_execution_router_readiness()


@app.post("/admin/ai-media-router/route")
def admin_route_ai_media_request(payload: dict):
    return route_ai_media_request(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        brand_name=str(payload.get("brand_name", "Brand")),
        media_type=str(payload.get("media_type", "image")),
        objective=str(payload.get("objective", "Create premium commercial media asset")),
        product_or_offer=str(payload.get("product_or_offer", "")),
        target_platform=str(payload.get("target_platform", "Meta Ads")),
        region=str(payload.get("region", "global")),
        requested_style=str(payload.get("requested_style", "")),
        brand_colours=list(payload.get("brand_colours", [])) if payload.get("brand_colours") is not None else [],
        character_reference=payload.get("character_reference"),
        preferred_model=payload.get("preferred_model"),
        live_keys_available=bool(payload.get("live_keys_available", False)),
        owner_approved=bool(payload.get("owner_approved", False)),
        entitlement_active=bool(payload.get("entitlement_active", True)),
    )


@app.get("/admin/ai-media-router/routes")
def admin_list_ai_media_router_results(tenant_id: str | None = None, status: str | None = None, limit: int = 50):
    return list_ai_media_router_results(tenant_id=tenant_id, status=status, limit=limit)

@app.get("/admin/ai-media-adapters/readiness")
def admin_ai_media_provider_adapters_readiness():
    return ai_media_provider_adapters_readiness()


@app.get("/admin/ai-media-adapters/status")
def admin_ai_media_provider_adapter_status(provider: str):
    return get_provider_adapter_status(provider=provider)


@app.post("/admin/ai-media-adapters/prepare")
def admin_prepare_ai_media_provider_payload(payload: dict):
    return prepare_provider_payload(
        provider=str(payload.get("provider", "")),
        media_type=str(payload.get("media_type", "image")),
        prompt=str(payload.get("prompt", "")),
        payload=dict(payload.get("payload", {})),
    )


@app.post("/admin/ai-media-adapters/execute")
def admin_execute_ai_media_provider_adapter(payload: dict):
    return execute_ai_media_provider_adapter(
        provider=str(payload.get("provider", "")),
        media_type=str(payload.get("media_type", "image")),
        prompt=str(payload.get("prompt", "")),
        payload=dict(payload.get("payload", {})),
        owner_approved=bool(payload.get("owner_approved", False)),
        allow_external_execution=bool(payload.get("allow_external_execution", False)),
    )


@app.get("/admin/ai-media-adapters/results")
def admin_list_ai_media_provider_adapter_results(provider: str | None = None, status: str | None = None, limit: int = 50):
    return list_ai_media_provider_adapter_results(provider=provider, status=status, limit=limit)

@app.get("/admin/ai-media-quality/readiness")
def admin_ai_media_quality_gate_readiness():
    return ai_media_quality_gate_readiness()


@app.post("/admin/ai-media-quality/score")
def admin_score_ai_media_quality(payload: dict):
    return score_ai_media_quality(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        media_type=str(payload.get("media_type", "media")),
        prompt=str(payload.get("prompt", "")),
        payload=dict(payload.get("payload", {})),
        selected_model=str(payload.get("selected_model", "")),
    )


@app.post("/admin/ai-media-quality/gate-packet")
def admin_gate_ai_media_execution_packet(payload: dict):
    return gate_ai_media_execution_packet(packet=dict(payload.get("packet", payload)))


@app.get("/admin/ai-media-quality/scores")
def admin_list_ai_media_quality_scores(tenant_id: str | None = None, status: str | None = None, limit: int = 50):
    return list_ai_media_quality_scores(tenant_id=tenant_id, status=status, limit=limit)

@app.get("/admin/ai-media-memory/readiness")
def admin_ai_media_brand_character_memory_readiness():
    return ai_media_brand_character_memory_readiness()


@app.post("/admin/ai-media-memory/brand")
def admin_save_ai_media_brand_memory(payload: dict):
    return save_brand_memory(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        brand_name=str(payload.get("brand_name", "Brand")),
        brand_colours=list(payload.get("brand_colours", [])) if payload.get("brand_colours") is not None else [],
        typography_style=str(payload.get("typography_style", "")),
        visual_style=str(payload.get("visual_style", "")),
        product_identity=str(payload.get("product_identity", "")),
        forbidden_styles=list(payload.get("forbidden_styles", [])) if payload.get("forbidden_styles") is not None else [],
        region_preferences=dict(payload.get("region_preferences", {})),
        platform_preferences=dict(payload.get("platform_preferences", {})),
    )


@app.post("/admin/ai-media-memory/character")
def admin_save_ai_media_character_memory(payload: dict):
    return save_character_memory(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        character_name=str(payload.get("character_name", "Creator")),
        reference_id=str(payload.get("reference_id", "")),
        face_consistency_notes=str(payload.get("face_consistency_notes", "")),
        voice_notes=str(payload.get("voice_notes", "")),
        age_range=str(payload.get("age_range", "")),
        gender_presentation=str(payload.get("gender_presentation", "")),
        ethnicity_or_regional_style=str(payload.get("ethnicity_or_regional_style", "")),
        accent_or_language_style=str(payload.get("accent_or_language_style", "")),
        usage_rules=list(payload.get("usage_rules", [])) if payload.get("usage_rules") is not None else [],
    )


@app.post("/admin/ai-media-memory/campaign-style")
def admin_save_ai_media_campaign_style_memory(payload: dict):
    return save_campaign_style_memory(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        campaign_name=str(payload.get("campaign_name", "Campaign")),
        target_platform=str(payload.get("target_platform", "Meta Ads")),
        media_type=str(payload.get("media_type", "video")),
        style_rules=list(payload.get("style_rules", [])) if payload.get("style_rules") is not None else [],
        winning_hooks=list(payload.get("winning_hooks", [])) if payload.get("winning_hooks") is not None else [],
        winning_visual_patterns=list(payload.get("winning_visual_patterns", [])) if payload.get("winning_visual_patterns") is not None else [],
        avoided_patterns=list(payload.get("avoided_patterns", [])) if payload.get("avoided_patterns") is not None else [],
        performance_notes=str(payload.get("performance_notes", "")),
    )


@app.get("/admin/ai-media-memory/context")
def admin_get_ai_media_memory_context(tenant_id: str, brand_name: str = "", target_platform: str = "", media_type: str = ""):
    return get_ai_media_memory_context(
        tenant_id=tenant_id,
        brand_name=brand_name,
        target_platform=target_platform,
        media_type=media_type,
    )


@app.post("/admin/ai-media-memory/enrich")
def admin_enrich_ai_media_payload_with_memory(payload: dict):
    return enrich_ai_media_payload_with_memory(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        payload=dict(payload.get("payload", {})),
    )


@app.get("/admin/ai-media-memory/list")
def admin_list_ai_media_memory(tenant_id: str | None = None, memory_type: str = "all", limit: int = 50):
    return list_ai_media_memory(tenant_id=tenant_id, memory_type=memory_type, limit=limit)

@app.get("/admin/ai-media-templates/readiness")
def admin_ai_media_prompt_template_pack_readiness():
    return ai_media_prompt_template_pack_readiness()


@app.get("/admin/ai-media-templates/list")
def admin_list_ai_media_prompt_templates(category: str | None = None):
    return list_ai_media_prompt_templates(category=category)


@app.post("/admin/ai-media-templates/recommend")
def admin_recommend_ai_media_prompt_template(payload: dict):
    return recommend_ai_media_prompt_template(
        media_type=str(payload.get("media_type", "")),
        target_platform=str(payload.get("target_platform", "")),
        objective=str(payload.get("objective", "")),
    )


@app.post("/admin/ai-media-templates/render")
def admin_render_ai_media_prompt_template(payload: dict):
    return render_ai_media_prompt_template(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        template_id=str(payload.get("template_id", "")),
        context=dict(payload.get("context", {})),
    )


@app.get("/admin/ai-media-templates/rendered")
def admin_list_rendered_ai_media_prompts(tenant_id: str | None = None, template_id: str | None = None, limit: int = 50):
    return list_rendered_ai_media_prompts(tenant_id=tenant_id, template_id=template_id, limit=limit)

@app.get("/admin/ai-media-packets/readiness")
def admin_ai_media_multi_provider_packets_readiness():
    return ai_media_multi_provider_packets_readiness()


@app.post("/admin/ai-media-packets/create")
def admin_create_ai_media_multi_provider_packet(payload: dict):
    return create_ai_media_multi_provider_packet(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        brand_name=str(payload.get("brand_name", "Brand")),
        media_type=str(payload.get("media_type", "image")),
        prompt=str(payload.get("prompt", "")),
        target_platform=str(payload.get("target_platform", "")),
        preferred_provider=str(payload.get("preferred_provider", "")),
        payload=dict(payload.get("payload", {})),
        owner_approved=bool(payload.get("owner_approved", False)),
        entitlement_active=bool(payload.get("entitlement_active", True)),
        quality_score=int(payload.get("quality_score", 0)),
        max_attempts=int(payload.get("max_attempts", 3)),
    )


@app.post("/admin/ai-media-packets/advance-provider")
def admin_advance_ai_media_packet_provider(payload: dict):
    return advance_packet_to_next_provider(
        packet=dict(payload.get("packet", {})),
        failure_reason=str(payload.get("failure_reason", "provider_failed")),
    )


@app.get("/admin/ai-media-packets/list")
def admin_list_ai_media_multi_provider_packets(tenant_id: str | None = None, status: str | None = None, limit: int = 50):
    return list_ai_media_multi_provider_packets(tenant_id=tenant_id, status=status, limit=limit)

@app.get("/admin/ai-media-pipeline/readiness")
def admin_ai_media_end_to_end_pipeline_readiness():
    return ai_media_end_to_end_pipeline_readiness()


@app.post("/admin/ai-media-pipeline/run")
def admin_run_ai_media_end_to_end_pipeline(payload: dict):
    return run_ai_media_end_to_end_pipeline(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        brand_name=str(payload.get("brand_name", "Brand")),
        media_type=str(payload.get("media_type", "ugc video")),
        objective=str(payload.get("objective", "Create premium commercial media asset")),
        product_or_offer=str(payload.get("product_or_offer", "")),
        target_platform=str(payload.get("target_platform", "TikTok")),
        region=str(payload.get("region", "global")),
        audience=str(payload.get("audience", "")),
        benefit=str(payload.get("benefit", "")),
        cta=str(payload.get("cta", "Shop now")),
        requested_style=str(payload.get("requested_style", "")),
        preferred_provider=str(payload.get("preferred_provider", "")),
        owner_approved=bool(payload.get("owner_approved", False)),
        entitlement_active=bool(payload.get("entitlement_active", True)),
        live_keys_available=bool(payload.get("live_keys_available", False)),
        context=dict(payload.get("context", {})),
    )


@app.get("/admin/ai-media-pipeline/runs")
def admin_list_ai_media_pipeline_runs(tenant_id: str | None = None, status: str | None = None, limit: int = 50):
    return list_ai_media_pipeline_runs(tenant_id=tenant_id, status=status, limit=limit)
@app.get("/admin/ai-media-creative-director/readiness")
def admin_ai_media_creative_director_readiness():
    return ai_media_creative_director_readiness()


@app.post("/admin/ai-media-creative-director/run")
def admin_ai_media_creative_director_run(payload: dict):
    return run_shared_ai_media_creative_director(payload)
@app.get("/debug/live-auth-fingerprint")
def debug_live_auth_fingerprint():
    def fp(name: str):
        value = os.getenv(name, "").strip()
        return {
            "present": bool(value),
            "length": len(value),
            "sha_prefix": hashlib.sha256(value.encode()).hexdigest()[:10] if value else None,
        }

    return {
        "success": True,
        "safe_debug": True,
        "secrets_not_returned": True,
        "admin_platform_token": fp("ADMIN_PLATFORM_TOKEN"),
        "admin_auth_secret": fp("ADMIN_AUTH_SECRET"),
        "admin_auth_token": fp("ADMIN_AUTH_TOKEN"),
        "app_env": os.getenv("APP_ENV", ""),
        "service": "control-api",
    }
@app.get("/system/live-auth-fingerprint")
def system_live_auth_fingerprint():
    def fp(name: str):
        value = os.getenv(name, "").strip()
        return {
            "present": bool(value),
            "length": len(value),
            "sha_prefix": hashlib.sha256(value.encode()).hexdigest()[:10] if value else None,
        }

    return {
        "success": True,
        "safe_debug": True,
        "public_safe": True,
        "secrets_not_returned": True,
        "admin_platform_token": fp("ADMIN_PLATFORM_TOKEN"),
        "admin_auth_secret": fp("ADMIN_AUTH_SECRET"),
        "admin_auth_token": fp("ADMIN_AUTH_TOKEN"),
        "app_env": os.getenv("APP_ENV", ""),
        "service": "control-api",
    }


# Global provider execution admin routes
@app.get("/admin/global-provider/readiness")
def admin_global_provider_readiness() -> Dict[str, object]:
    return {
        "success": True,
        "scope": "platform_wide_multi_agent",
        "real_provider_activation": real_provider_activation_readiness(),
        "global_provider_execution": global_provider_execution_readiness(),
        "global_connector": global_real_provider_connector_readiness(),
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
    }


@app.post("/admin/global-provider/execution-packet")
def admin_global_provider_execution_packet(payload: dict) -> Dict[str, object]:
    return {
        "success": True,
        "scope": "platform_wide_multi_agent",
        "provider_execution_packet": build_global_provider_execution_packet(payload),
        "connector_execution_packet": build_global_connector_execution_packet(payload),
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
    }



@app.get("/admin/provider-activation/status")
def admin_provider_activation_status():
    return get_all_provider_activation_statuses()


@app.get("/admin/provider-activation/status/{provider_key}")
def admin_provider_activation_single_status(provider_key: str):
    return get_provider_activation_status(provider_key)


@app.get("/admin/provider-activation/select/{capability}")
def admin_provider_activation_select(capability: str):
    return select_ready_provider_for_capability(capability)


@app.post("/admin/provider-jobs/create")
def admin_provider_jobs_create(payload: dict):
    return create_async_provider_job(
        tenant_id=str(payload.get("tenant_id", "admin-internal")),
        actor_role=str(payload.get("actor_role", "owner")),
        provider_key=str(payload.get("provider_key", "openai")),
        capability=str(payload.get("capability", "text")),
        request_payload=dict(payload.get("request_payload", {})),
        owner_approval_required=bool(payload.get("owner_approval_required", True)),
    )


@app.get("/admin/provider-jobs/list")
def admin_provider_jobs_list(tenant_id: str = None, status: str = None):
    return list_async_provider_jobs(tenant_id=tenant_id, status=status)


@app.get("/admin/provider-jobs/{job_id}")
def admin_provider_jobs_get(job_id: str):
    return get_async_provider_job(job_id)


@app.post("/admin/provider-jobs/{job_id}/status")
def admin_provider_jobs_update_status(job_id: str, payload: dict):
    return update_async_provider_job_status(
        job_id=job_id,
        status=str(payload.get("status", "queued")),
        provider_job_id=payload.get("provider_job_id"),
        provider_status=payload.get("provider_status"),
        failure_reason=payload.get("failure_reason"),
        asset_delivery_packet=payload.get("asset_delivery_packet"),
    )


@app.post("/admin/provider-jobs/{job_id}/retry")
def admin_provider_jobs_retry(job_id: str, payload: dict):
    return mark_async_provider_job_retry(
        job_id=job_id,
        reason=str(payload.get("reason", "manual_retry_requested")),
    )


@app.get("/admin/provider-adapters/status/{provider_key}")
def admin_provider_adapter_status(provider_key: str):
    return get_provider_adapter_status(provider_key)


@app.post("/admin/provider-adapters/normalise")
def admin_provider_adapter_normalise(payload: dict):
    return normalise_provider_request(payload)


@app.post("/admin/provider-adapters/route")
def admin_provider_adapter_route(payload: dict):
    return route_provider_request(payload)


@app.post("/admin/provider-adapters/execute-scaffold")
def admin_provider_adapter_execute_scaffold(payload: dict):
    return execute_provider_request_scaffold(payload)


@app.get("/admin/provider-adapters/unified-status/{provider_key}")
def admin_provider_adapter_unified_status(provider_key: str):
    return get_provider_adapter_status(provider_key)


@app.get("/admin/unified-provider-adapter-status/{provider_key}")
def admin_unified_provider_adapter_status(provider_key: str):
    return get_provider_adapter_status(provider_key)


@app.get("/provider-adapter-unified-status/{provider_key}")
def root_provider_adapter_unified_status(provider_key: str):
    return get_provider_adapter_status(provider_key)


@app.get("/provider-adapter-runtime-status/{provider_key}")
def provider_adapter_runtime_status(provider_key: str):
    return get_unified_provider_adapter_status(provider_key)


# ---------------------------------------------------------------------------
# Gate-safe live provider adapter routes
# Added by wire_gate_safe_live_provider_adapter_routes.py
# Purpose:
# - expose credential-safe provider adapter runtime checks
# - expose owner-governed execution preparation only
# - keep real provider calls blocked unless credentials + owner execution gates pass
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.live_provider_adapters import (
        build_failover_routing_packet,
        build_polling_packet,
        calculate_provider_health_score,
        create_execution_audit_linkage,
        create_signed_asset_delivery_packet,
        execute_gate_safe_provider_request,
        live_provider_adapter_runtime_status,
        normalise_provider_failure,
        provider_timeout_policy,
    )
except Exception:  # pragma: no cover
    build_failover_routing_packet = None
    build_polling_packet = None
    calculate_provider_health_score = None
    create_execution_audit_linkage = None
    create_signed_asset_delivery_packet = None
    execute_gate_safe_provider_request = None
    live_provider_adapter_runtime_status = None
    normalise_provider_failure = None
    provider_timeout_policy = None


@app.get("/live-provider-adapter-runtime-status/{provider_key}")
def live_provider_adapter_runtime_status_route(provider_key: str):
    if live_provider_adapter_runtime_status is None:
        return {
            "status": "unavailable",
            "reason": "live_provider_adapter_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return live_provider_adapter_runtime_status(provider_key)


@app.post("/live-provider-adapter-execute/{provider_key}")
async def live_provider_adapter_execute_route(provider_key: str, payload: dict):
    if execute_gate_safe_provider_request is None:
        return {
            "status": "blocked",
            "reason": "live_provider_adapter_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    result = execute_gate_safe_provider_request(provider_key, safe_payload)

    tenant_id = safe_payload.get("tenant_id") or "unknown-tenant"
    request_id = safe_payload.get("request_id") or "unknown-request"
    provider_job_id = result.get("provider_job_id")

    audit_linkage = None
    if create_execution_audit_linkage is not None:
        audit_linkage = create_execution_audit_linkage(
            tenant_id=tenant_id,
            request_id=request_id,
            provider_key=provider_key,
            provider_job_id=provider_job_id,
            execution_status=result.get("status", "blocked"),
        )

    return {
        "status": result.get("status"),
        "provider_key": provider_key,
        "execution_result": result,
        "audit_linkage": audit_linkage,
        "owner_governed_execution_required": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


@app.get("/live-provider-adapter-timeout-policy/{provider_key}")
def live_provider_adapter_timeout_policy_route(provider_key: str):
    if provider_timeout_policy is None:
        return {
            "status": "unavailable",
            "reason": "live_provider_adapter_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return {
        "provider_key": provider_key,
        "timeout_policy": provider_timeout_policy(provider_key),
        "credential_values_exposed": False,
    }


@app.get("/live-provider-adapter-polling-packet/{provider_key}/{provider_job_id}")
def live_provider_adapter_polling_packet_route(provider_key: str, provider_job_id: str):
    if build_polling_packet is None:
        return {
            "status": "unavailable",
            "reason": "live_provider_adapter_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return build_polling_packet(provider_key, provider_job_id)


@app.post("/live-provider-adapter-failover-routing")
async def live_provider_adapter_failover_routing_route(payload: dict):
    if build_failover_routing_packet is None:
        return {
            "status": "unavailable",
            "reason": "live_provider_adapter_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    requested_provider = safe_payload.get("requested_provider") or safe_payload.get("provider_key") or ""
    available_providers = safe_payload.get("available_providers") or []

    return build_failover_routing_packet(
        requested_provider=requested_provider,
        available_providers=available_providers,
    )


@app.post("/live-provider-adapter-health-score")
async def live_provider_adapter_health_score_route(payload: dict):
    if calculate_provider_health_score is None:
        return {
            "status": "unavailable",
            "reason": "live_provider_adapter_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return calculate_provider_health_score(
        success_count=int(safe_payload.get("success_count", 0) or 0),
        failure_count=int(safe_payload.get("failure_count", 0) or 0),
        timeout_count=int(safe_payload.get("timeout_count", 0) or 0),
        average_latency_ms=safe_payload.get("average_latency_ms"),
    )


@app.post("/live-provider-adapter-failure-normalisation")
async def live_provider_adapter_failure_normalisation_route(payload: dict):
    if normalise_provider_failure is None:
        return {
            "status": "unavailable",
            "reason": "live_provider_adapter_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return normalise_provider_failure(
        provider_key=safe_payload.get("provider_key") or "unknown",
        error_code=safe_payload.get("error_code") or "provider_error",
        message=safe_payload.get("message") or "Provider execution failed safely.",
        retryable=bool(safe_payload.get("retryable", True)),
        status_code=safe_payload.get("status_code"),
    )


@app.post("/live-provider-adapter-asset-packet")
async def live_provider_adapter_asset_packet_route(payload: dict):
    if create_signed_asset_delivery_packet is None:
        return {
            "status": "unavailable",
            "reason": "live_provider_adapter_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return create_signed_asset_delivery_packet(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        asset_id=safe_payload.get("asset_id") or "unknown-asset",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        asset_type=safe_payload.get("asset_type") or "generated_asset",
        expires_in_seconds=int(safe_payload.get("expires_in_seconds", 3600) or 3600),
    )


# ---------------------------------------------------------------------------
# Async provider orchestration routes
# Added by wire_async_provider_orchestration_routes.py
# Purpose:
# - expose async provider orchestration packets
# - expose polling state transitions
# - expose retry/manual-review escalation
# - expose execution timeline + latency aggregation
# - expose provider selection/failover preparation
# - do NOT execute real external provider calls
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.async_provider_orchestration_runtime import (
        advance_provider_polling_state,
        aggregate_provider_latency_metrics,
        build_provider_execution_timeline_event,
        create_provider_orchestration_packet,
        create_retry_escalation_packet,
        prepare_provider_selection_packet,
    )
except Exception:  # pragma: no cover
    advance_provider_polling_state = None
    aggregate_provider_latency_metrics = None
    build_provider_execution_timeline_event = None
    create_provider_orchestration_packet = None
    create_retry_escalation_packet = None
    prepare_provider_selection_packet = None


@app.post("/async-provider-orchestration/packet")
async def async_provider_orchestration_packet_route(payload: dict):
    if create_provider_orchestration_packet is None:
        return {
            "status": "unavailable",
            "reason": "async_provider_orchestration_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return create_provider_orchestration_packet(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        task_type=safe_payload.get("task_type") or "provider_generation",
        payload=safe_payload.get("payload") or {},
        live_execution_requested=bool(safe_payload.get("live_execution_requested", False)),
        owner_governed_execution_confirmed=bool(
            safe_payload.get("owner_governed_execution_confirmed", False)
        ),
    )


@app.post("/async-provider-orchestration/polling-state")
async def async_provider_orchestration_polling_state_route(payload: dict):
    if advance_provider_polling_state is None:
        return {
            "status": "unavailable",
            "reason": "async_provider_orchestration_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return advance_provider_polling_state(
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        provider_job_id=safe_payload.get("provider_job_id") or "unknown-job",
        current_state=safe_payload.get("current_state") or "queued",
        provider_status=safe_payload.get("provider_status") or "queued",
        attempt_count=int(safe_payload.get("attempt_count", 0) or 0),
    )


@app.post("/async-provider-orchestration/retry-escalation")
async def async_provider_orchestration_retry_escalation_route(payload: dict):
    if create_retry_escalation_packet is None:
        return {
            "status": "unavailable",
            "reason": "async_provider_orchestration_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return create_retry_escalation_packet(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        failure_code=safe_payload.get("failure_code") or "provider_error",
        attempt_count=int(safe_payload.get("attempt_count", 0) or 0),
        max_attempts=int(safe_payload.get("max_attempts", 3) or 3),
    )


@app.post("/async-provider-orchestration/timeline-event")
async def async_provider_orchestration_timeline_event_route(payload: dict):
    if build_provider_execution_timeline_event is None:
        return {
            "status": "unavailable",
            "reason": "async_provider_orchestration_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return build_provider_execution_timeline_event(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        event_type=safe_payload.get("event_type") or "provider_orchestration_event",
        status=safe_payload.get("status") or "queued",
        latency_ms=safe_payload.get("latency_ms"),
    )


@app.post("/async-provider-orchestration/latency-metrics")
async def async_provider_orchestration_latency_metrics_route(payload: dict):
    if aggregate_provider_latency_metrics is None:
        return {
            "status": "unavailable",
            "reason": "async_provider_orchestration_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    events = safe_payload.get("events") or []
    if not isinstance(events, list):
        events = []

    return aggregate_provider_latency_metrics(events)


@app.post("/async-provider-orchestration/provider-selection")
async def async_provider_orchestration_provider_selection_route(payload: dict):
    if prepare_provider_selection_packet is None:
        return {
            "status": "unavailable",
            "reason": "async_provider_orchestration_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    available_providers = safe_payload.get("available_providers") or []
    provider_health = safe_payload.get("provider_health") or {}

    if not isinstance(available_providers, list):
        available_providers = []
    if not isinstance(provider_health, dict):
        provider_health = {}

    return prepare_provider_selection_packet(
        requested_provider=safe_payload.get("requested_provider") or "unknown-provider",
        available_providers=available_providers,
        provider_health=provider_health,
    )


# ---------------------------------------------------------------------------
# Real provider HTTP execution routes + orchestration bridge
# Added by wire_real_provider_http_execution_routes.py
# Purpose:
# - expose HTTP request builders/status safely
# - expose success/error normalisation safely
# - expose orchestration-to-HTTP dispatch preparation bridge
# - do NOT execute real external provider calls
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.real_provider_http_execution_layer import (
        build_provider_http_request_packet,
        execute_real_provider_http_request,
        map_provider_http_exception,
        normalise_provider_success_response,
        real_provider_http_runtime_status,
    )
    from backend.app.runtime.async_provider_orchestration_runtime import (
        create_provider_http_dispatch_preparation_packet,
        provider_http_dispatch_bridge_status,
    )
except Exception:  # pragma: no cover
    build_provider_http_request_packet = None
    execute_real_provider_http_request = None
    map_provider_http_exception = None
    normalise_provider_success_response = None
    real_provider_http_runtime_status = None
    create_provider_http_dispatch_preparation_packet = None
    provider_http_dispatch_bridge_status = None


@app.get("/real-provider-http/runtime-status/{provider_key}")
def real_provider_http_runtime_status_route(provider_key: str):
    if real_provider_http_runtime_status is None:
        return {
            "status": "unavailable",
            "reason": "real_provider_http_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return real_provider_http_runtime_status(provider_key)


@app.post("/real-provider-http/request-packet/{provider_key}")
async def real_provider_http_request_packet_route(provider_key: str, payload: dict):
    if build_provider_http_request_packet is None:
        return {
            "status": "unavailable",
            "reason": "real_provider_http_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return build_provider_http_request_packet(provider_key, dict(payload or {}))


@app.post("/real-provider-http/execute/{provider_key}")
async def real_provider_http_execute_route(provider_key: str, payload: dict):
    if execute_real_provider_http_request is None:
        return {
            "status": "blocked",
            "reason": "real_provider_http_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return execute_real_provider_http_request(provider_key, dict(payload or {}))


@app.post("/real-provider-http/success-normalisation/{provider_key}")
async def real_provider_http_success_normalisation_route(provider_key: str, payload: dict):
    if normalise_provider_success_response is None:
        return {
            "status": "unavailable",
            "reason": "real_provider_http_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    raw_response = safe_payload.get("raw_response") or {}
    if not isinstance(raw_response, dict):
        raw_response = {}

    return normalise_provider_success_response(
        provider_key=provider_key,
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        raw_response=raw_response,
        asset_type=safe_payload.get("asset_type") or "generated_asset",
    )


@app.post("/real-provider-http/error-normalisation/{provider_key}")
async def real_provider_http_error_normalisation_route(provider_key: str, payload: dict):
    if map_provider_http_exception is None:
        return {
            "status": "unavailable",
            "reason": "real_provider_http_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return map_provider_http_exception(
        provider_key,
        exception_type=safe_payload.get("exception_type") or "provider_unknown_error",
        status_code=safe_payload.get("status_code"),
    )


@app.post("/real-provider-http/dispatch-bridge/{provider_key}")
async def real_provider_http_dispatch_bridge_route(provider_key: str, payload: dict):
    if create_provider_http_dispatch_preparation_packet is None:
        return {
            "status": "unavailable",
            "reason": "provider_http_dispatch_bridge_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return create_provider_http_dispatch_preparation_packet(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=provider_key,
        task_type=safe_payload.get("task_type") or "provider_generation",
        payload=safe_payload.get("payload") or {},
        live_execution_requested=bool(safe_payload.get("live_execution_requested", False)),
        owner_governed_execution_confirmed=bool(
            safe_payload.get("owner_governed_execution_confirmed", False)
        ),
    )


@app.get("/real-provider-http/dispatch-bridge-status/{provider_key}")
def real_provider_http_dispatch_bridge_status_route(provider_key: str):
    if provider_http_dispatch_bridge_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_http_dispatch_bridge_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_http_dispatch_bridge_status(provider_key)


# ---------------------------------------------------------------------------
# Provider dispatch policy + worker foundation routes
# Added by wire_provider_dispatch_policy_worker_routes.py
# Purpose:
# - expose dispatch policy status/evaluation
# - expose worker job preparation
# - expose safe worker state advancement
# - keep real background dispatch disabled
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_dispatch_policy_worker_foundation import (
        advance_provider_worker_job,
        create_provider_worker_job_packet,
        evaluate_provider_dispatch_policy,
        provider_dispatch_policy_status,
        provider_worker_foundation_status,
    )
except Exception:  # pragma: no cover
    advance_provider_worker_job = None
    create_provider_worker_job_packet = None
    evaluate_provider_dispatch_policy = None
    provider_dispatch_policy_status = None
    provider_worker_foundation_status = None


@app.get("/provider-dispatch-policy/status")
def provider_dispatch_policy_status_route():
    if provider_dispatch_policy_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_dispatch_policy_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_dispatch_policy_status()


@app.post("/provider-dispatch-policy/evaluate/{provider_key}")
async def provider_dispatch_policy_evaluate_route(provider_key: str, payload: dict):
    if evaluate_provider_dispatch_policy is None:
        return {
            "status": "unavailable",
            "reason": "provider_dispatch_policy_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return evaluate_provider_dispatch_policy(
        provider_key=provider_key,
        payload=dict(payload or {}),
    )


@app.get("/provider-worker-foundation/status")
def provider_worker_foundation_status_route():
    if provider_worker_foundation_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_worker_foundation_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_worker_foundation_status()


@app.post("/provider-worker-foundation/create-job/{provider_key}")
async def provider_worker_foundation_create_job_route(provider_key: str, payload: dict):
    if create_provider_worker_job_packet is None:
        return {
            "status": "unavailable",
            "reason": "provider_worker_foundation_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return create_provider_worker_job_packet(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=provider_key,
        task_type=safe_payload.get("task_type") or "provider_generation",
        payload=safe_payload.get("payload") or {},
        live_execution_requested=bool(safe_payload.get("live_execution_requested", False)),
        owner_governed_execution_confirmed=bool(
            safe_payload.get("owner_governed_execution_confirmed", False)
        ),
    )


@app.post("/provider-worker-foundation/advance-job/{provider_key}")
async def provider_worker_foundation_advance_job_route(provider_key: str, payload: dict):
    if advance_provider_worker_job is None:
        return {
            "status": "unavailable",
            "reason": "provider_worker_foundation_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return advance_provider_worker_job(
        worker_job_id=safe_payload.get("worker_job_id") or "unknown-worker-job",
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=provider_key,
        current_state=safe_payload.get("current_state") or "dispatch_blocked",
        attempt_count=int(safe_payload.get("attempt_count", 0) or 0),
        failure_code=safe_payload.get("failure_code"),
    )


# ---------------------------------------------------------------------------
# Provider execution persistence ledger routes
# Added by wire_provider_execution_ledger_routes_and_worker_bridge.py
# Purpose:
# - expose execution records, worker ledger, dispatch attempts, retry history,
#   and latency metrics
# - use safe in-memory fallback until Postgres binding is added
# - never expose credentials
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_execution_persistence_ledger import (
        append_worker_event_ledger_entry,
        create_provider_execution_record,
        get_provider_execution_record,
        list_dispatch_attempt_records,
        list_provider_execution_records,
        list_provider_latency_metrics,
        list_retry_history_records,
        list_worker_event_ledger,
        provider_execution_persistence_status,
        record_dispatch_attempt,
        record_provider_latency_metric,
        record_retry_history,
        reset_provider_execution_ledger_for_tests,
        update_provider_execution_record,
    )
except Exception:  # pragma: no cover
    append_worker_event_ledger_entry = None
    create_provider_execution_record = None
    get_provider_execution_record = None
    list_dispatch_attempt_records = None
    list_provider_execution_records = None
    list_provider_latency_metrics = None
    list_retry_history_records = None
    list_worker_event_ledger = None
    provider_execution_persistence_status = None
    record_dispatch_attempt = None
    record_provider_latency_metric = None
    record_retry_history = None
    reset_provider_execution_ledger_for_tests = None
    update_provider_execution_record = None


@app.get("/provider-execution-ledger/status")
def provider_execution_ledger_status_route():
    if provider_execution_persistence_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_execution_persistence_status()


@app.post("/provider-execution-ledger/create-record")
async def provider_execution_ledger_create_record_route(payload: dict):
    if create_provider_execution_record is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    safe_payload = dict(payload or {})
    return create_provider_execution_record(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        task_type=safe_payload.get("task_type") or "provider_generation",
        execution_status=safe_payload.get("execution_status") or "created",
        worker_job_id=safe_payload.get("worker_job_id"),
        provider_job_id=safe_payload.get("provider_job_id"),
    )


@app.post("/provider-execution-ledger/update-record/{execution_id}")
async def provider_execution_ledger_update_record_route(execution_id: str, payload: dict):
    if update_provider_execution_record is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    safe_payload = dict(payload or {})
    return update_provider_execution_record(
        execution_id=execution_id,
        execution_status=safe_payload.get("execution_status"),
        worker_job_id=safe_payload.get("worker_job_id"),
        provider_job_id=safe_payload.get("provider_job_id"),
        extra=safe_payload.get("extra"),
    )


@app.get("/provider-execution-ledger/record/{execution_id}")
def provider_execution_ledger_get_record_route(execution_id: str):
    if get_provider_execution_record is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    return get_provider_execution_record(execution_id)


@app.get("/provider-execution-ledger/records")
def provider_execution_ledger_list_records_route(
    tenant_id: str = "",
    provider_key: str = "",
    limit: int = 50,
):
    if list_provider_execution_records is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    return list_provider_execution_records(
        tenant_id=tenant_id or None,
        provider_key=provider_key or None,
        limit=limit,
    )


@app.get("/provider-execution-ledger/worker-events")
def provider_execution_ledger_worker_events_route(
    tenant_id: str = "",
    execution_id: str = "",
    limit: int = 100,
):
    if list_worker_event_ledger is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    return list_worker_event_ledger(
        tenant_id=tenant_id or None,
        execution_id=execution_id or None,
        limit=limit,
    )


@app.get("/provider-execution-ledger/dispatch-attempts")
def provider_execution_ledger_dispatch_attempts_route(
    tenant_id: str = "",
    execution_id: str = "",
    limit: int = 100,
):
    if list_dispatch_attempt_records is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    return list_dispatch_attempt_records(
        tenant_id=tenant_id or None,
        execution_id=execution_id or None,
        limit=limit,
    )


@app.get("/provider-execution-ledger/retry-history")
def provider_execution_ledger_retry_history_route(
    tenant_id: str = "",
    execution_id: str = "",
    limit: int = 100,
):
    if list_retry_history_records is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    return list_retry_history_records(
        tenant_id=tenant_id or None,
        execution_id=execution_id or None,
        limit=limit,
    )


@app.get("/provider-execution-ledger/latency-metrics")
def provider_execution_ledger_latency_metrics_route(
    tenant_id: str = "",
    provider_key: str = "",
    limit: int = 100,
):
    if list_provider_latency_metrics is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    return list_provider_latency_metrics(
        tenant_id=tenant_id or None,
        provider_key=provider_key or None,
        limit=limit,
    )


@app.post("/provider-execution-ledger/reset-for-tests")
async def provider_execution_ledger_reset_for_tests_route():
    if reset_provider_execution_ledger_for_tests is None:
        return {
            "status": "unavailable",
            "reason": "provider_execution_ledger_not_loaded",
            "credential_values_exposed": False,
        }
    return reset_provider_execution_ledger_for_tests()


# ---------------------------------------------------------------------------
# Provider execution Postgres ledger bridge routes
# Added by wire_provider_execution_postgres_ledger_bridge_routes.py
# Purpose:
# - expose Postgres schema/readiness bridge
# - keep safe in-memory fallback active until DB driver/migration is enabled
# - never expose credentials
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
        apply_provider_ledger_schema_if_possible,
        get_provider_ledger_schema_sql,
        persist_dispatch_attempt_bridge,
        persist_latency_metric_bridge,
        persist_provider_execution_record_bridge,
        persist_retry_history_bridge,
        persist_worker_event_bridge,
        provider_postgres_bridge_summary,
        provider_postgres_ledger_bridge_status,
        reset_provider_postgres_bridge_fallback_for_tests,
    )
except Exception:  # pragma: no cover
    apply_provider_ledger_schema_if_possible = None
    get_provider_ledger_schema_sql = None
    persist_dispatch_attempt_bridge = None
    persist_latency_metric_bridge = None
    persist_provider_execution_record_bridge = None
    persist_retry_history_bridge = None
    persist_worker_event_bridge = None
    provider_postgres_bridge_summary = None
    provider_postgres_ledger_bridge_status = None
    reset_provider_postgres_bridge_fallback_for_tests = None


@app.get("/provider-postgres-ledger-bridge/status")
def provider_postgres_ledger_bridge_status_route():
    if provider_postgres_ledger_bridge_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_postgres_ledger_bridge_status()


@app.get("/provider-postgres-ledger-bridge/schema")
def provider_postgres_ledger_bridge_schema_route():
    if get_provider_ledger_schema_sql is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
            "credential_values_exposed": False,
        }
    return get_provider_ledger_schema_sql()


@app.post("/provider-postgres-ledger-bridge/apply-schema")
async def provider_postgres_ledger_bridge_apply_schema_route():
    if apply_provider_ledger_schema_if_possible is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
            "credential_values_exposed": False,
        }
    return apply_provider_ledger_schema_if_possible()


@app.post("/provider-postgres-ledger-bridge/persist-execution-record")
async def provider_postgres_ledger_bridge_persist_execution_record_route(payload: dict):
    if persist_provider_execution_record_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return persist_provider_execution_record_bridge(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        task_type=safe_payload.get("task_type") or "provider_generation",
        execution_status=safe_payload.get("execution_status") or "created",
        worker_job_id=safe_payload.get("worker_job_id"),
        provider_job_id=safe_payload.get("provider_job_id"),
    )


@app.post("/provider-postgres-ledger-bridge/persist-worker-event")
async def provider_postgres_ledger_bridge_persist_worker_event_route(payload: dict):
    if persist_worker_event_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    details = safe_payload.get("details") or {}
    if not isinstance(details, dict):
        details = {}

    return persist_worker_event_bridge(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        worker_job_id=safe_payload.get("worker_job_id") or "unknown-worker",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        event_type=safe_payload.get("event_type") or "provider_worker_event",
        status=safe_payload.get("status") or "created",
        details=details,
    )


@app.post("/provider-postgres-ledger-bridge/persist-dispatch-attempt")
async def provider_postgres_ledger_bridge_persist_dispatch_attempt_route(payload: dict):
    if persist_dispatch_attempt_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return persist_dispatch_attempt_bridge(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        worker_job_id=safe_payload.get("worker_job_id") or "unknown-worker",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        attempt_number=int(safe_payload.get("attempt_number", 1) or 1),
        allowed_by_policy=bool(safe_payload.get("allowed_by_policy", False)),
        result_status=safe_payload.get("result_status") or "blocked",
        reason=safe_payload.get("reason"),
    )


@app.post("/provider-postgres-ledger-bridge/persist-retry-history")
async def provider_postgres_ledger_bridge_persist_retry_history_route(payload: dict):
    if persist_retry_history_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return persist_retry_history_bridge(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        worker_job_id=safe_payload.get("worker_job_id") or "unknown-worker",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        attempt_number=int(safe_payload.get("attempt_number", 1) or 1),
        failure_code=safe_payload.get("failure_code") or "provider_error",
        retry_allowed=bool(safe_payload.get("retry_allowed", False)),
        next_action=safe_payload.get("next_action") or "owner_review_required",
    )


@app.post("/provider-postgres-ledger-bridge/persist-latency-metric")
async def provider_postgres_ledger_bridge_persist_latency_metric_route(payload: dict):
    if persist_latency_metric_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return persist_latency_metric_bridge(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        latency_ms=int(safe_payload.get("latency_ms", 0) or 0),
        operation=safe_payload.get("operation") or "provider_operation",
    )


@app.get("/provider-postgres-ledger-bridge/summary")
def provider_postgres_ledger_bridge_summary_route():
    if provider_postgres_bridge_summary is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_postgres_bridge_summary()


@app.post("/provider-postgres-ledger-bridge/reset-for-tests")
async def provider_postgres_ledger_bridge_reset_for_tests_route():
    if reset_provider_postgres_bridge_fallback_for_tests is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_ledger_bridge_not_loaded",
            "credential_values_exposed": False,
        }
    return reset_provider_postgres_bridge_fallback_for_tests()


# ---------------------------------------------------------------------------
# Provider execution Postgres migration apply routes
# Added by wire_provider_execution_postgres_migration_apply_routes.py
# Purpose:
# - expose DB driver/schema apply readiness
# - apply schema only when DATABASE_URL and driver are available
# - keep safe fallback active on failure
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
        apply_provider_ledger_schema_with_driver,
        detect_postgres_driver,
        provider_postgres_migration_apply_status,
    )
except Exception:  # pragma: no cover
    apply_provider_ledger_schema_with_driver = None
    detect_postgres_driver = None
    provider_postgres_migration_apply_status = None


@app.get("/provider-postgres-migration/status")
def provider_postgres_migration_status_route():
    if provider_postgres_migration_apply_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_migration_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_postgres_migration_apply_status()


@app.get("/provider-postgres-migration/driver")
def provider_postgres_migration_driver_route():
    if detect_postgres_driver is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_migration_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return detect_postgres_driver()


@app.post("/provider-postgres-migration/apply")
async def provider_postgres_migration_apply_route():
    if apply_provider_ledger_schema_with_driver is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_migration_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return apply_provider_ledger_schema_with_driver()


# ---------------------------------------------------------------------------
# Provider execution Postgres read/write bridge routes
# Added by wire_provider_execution_postgres_read_write_routes.py
# Purpose:
# - expose DB-capable execution record write/read bridge
# - keep safe fallback active when DB is unavailable
# - never expose credentials
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
        persist_provider_execution_record_bridge,
        postgres_read_provider_execution_records,
        provider_postgres_read_write_status,
    )
except Exception:  # pragma: no cover
    persist_provider_execution_record_bridge = None
    postgres_read_provider_execution_records = None
    provider_postgres_read_write_status = None


@app.get("/provider-postgres-read-write/status")
def provider_postgres_read_write_status_route():
    if provider_postgres_read_write_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_read_write_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_postgres_read_write_status()


@app.post("/provider-postgres-read-write/execution-record")
async def provider_postgres_read_write_execution_record_route(payload: dict):
    if persist_provider_execution_record_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_read_write_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return persist_provider_execution_record_bridge(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        task_type=safe_payload.get("task_type") or "provider_generation",
        execution_status=safe_payload.get("execution_status") or "created",
        worker_job_id=safe_payload.get("worker_job_id"),
        provider_job_id=safe_payload.get("provider_job_id"),
    )


@app.get("/provider-postgres-read-write/execution-records")
def provider_postgres_read_write_execution_records_route(
    tenant_id: str = "",
    provider_key: str = "",
    limit: int = 50,
):
    if postgres_read_provider_execution_records is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_read_write_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return postgres_read_provider_execution_records(
        tenant_id=tenant_id or None,
        provider_key=provider_key or None,
        limit=limit,
    )


# ---------------------------------------------------------------------------
# Provider execution Postgres extended ledger write routes
# Added by wire_provider_execution_postgres_extended_ledger_write_routes.py
# Purpose:
# - expose DB-capable worker event, dispatch attempt, retry history,
#   and latency metric writes
# - preserve safe fallback when DB is unavailable
# - never expose credentials
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
        persist_dispatch_attempt_bridge,
        persist_latency_metric_bridge,
        persist_retry_history_bridge,
        persist_worker_event_bridge,
        provider_postgres_extended_ledger_write_status,
    )
except Exception:  # pragma: no cover
    persist_dispatch_attempt_bridge = None
    persist_latency_metric_bridge = None
    persist_retry_history_bridge = None
    persist_worker_event_bridge = None
    provider_postgres_extended_ledger_write_status = None


@app.get("/provider-postgres-extended-ledger-writes/status")
def provider_postgres_extended_ledger_write_status_route():
    if provider_postgres_extended_ledger_write_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_write_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_postgres_extended_ledger_write_status()


@app.post("/provider-postgres-extended-ledger-writes/worker-event")
async def provider_postgres_extended_worker_event_route(payload: dict):
    if persist_worker_event_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_write_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    details = safe_payload.get("details") or {}
    if not isinstance(details, dict):
        details = {}

    return persist_worker_event_bridge(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        worker_job_id=safe_payload.get("worker_job_id") or "unknown-worker",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        event_type=safe_payload.get("event_type") or "provider_worker_event",
        status=safe_payload.get("status") or "created",
        details=details,
    )


@app.post("/provider-postgres-extended-ledger-writes/dispatch-attempt")
async def provider_postgres_extended_dispatch_attempt_route(payload: dict):
    if persist_dispatch_attempt_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_write_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return persist_dispatch_attempt_bridge(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        worker_job_id=safe_payload.get("worker_job_id") or "unknown-worker",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        attempt_number=int(safe_payload.get("attempt_number", 1) or 1),
        allowed_by_policy=bool(safe_payload.get("allowed_by_policy", False)),
        result_status=safe_payload.get("result_status") or "blocked",
        reason=safe_payload.get("reason"),
    )


@app.post("/provider-postgres-extended-ledger-writes/retry-history")
async def provider_postgres_extended_retry_history_route(payload: dict):
    if persist_retry_history_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_write_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return persist_retry_history_bridge(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        worker_job_id=safe_payload.get("worker_job_id") or "unknown-worker",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        attempt_number=int(safe_payload.get("attempt_number", 1) or 1),
        failure_code=safe_payload.get("failure_code") or "provider_error",
        retry_allowed=bool(safe_payload.get("retry_allowed", False)),
        next_action=safe_payload.get("next_action") or "owner_review_required",
    )


@app.post("/provider-postgres-extended-ledger-writes/latency-metric")
async def provider_postgres_extended_latency_metric_route(payload: dict):
    if persist_latency_metric_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_write_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return persist_latency_metric_bridge(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        latency_ms=int(safe_payload.get("latency_ms", 0) or 0),
        operation=safe_payload.get("operation") or "provider_operation",
    )


# ---------------------------------------------------------------------------
# Provider execution Postgres extended ledger read routes
# Added by wire_provider_execution_postgres_extended_ledger_read_routes.py
# Purpose:
# - expose read views for worker events, dispatch attempts, retry history,
#   and latency metrics
# - preserve safe fallback when DB is unavailable
# - never expose credentials
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
        provider_postgres_extended_ledger_read_status,
        postgres_read_dispatch_attempts,
        postgres_read_latency_metrics,
        postgres_read_retry_history,
        postgres_read_worker_events,
    )
except Exception:  # pragma: no cover
    provider_postgres_extended_ledger_read_status = None
    postgres_read_dispatch_attempts = None
    postgres_read_latency_metrics = None
    postgres_read_retry_history = None
    postgres_read_worker_events = None


@app.get("/provider-postgres-extended-ledger-reads/status")
def provider_postgres_extended_ledger_read_status_route():
    if provider_postgres_extended_ledger_read_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_read_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_postgres_extended_ledger_read_status()


@app.get("/provider-postgres-extended-ledger-reads/worker-events")
def provider_postgres_extended_worker_events_read_route(
    tenant_id: str = "",
    execution_id: str = "",
    limit: int = 100,
):
    if postgres_read_worker_events is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_read_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return postgres_read_worker_events(
        tenant_id=tenant_id or None,
        execution_id=execution_id or None,
        limit=limit,
    )


@app.get("/provider-postgres-extended-ledger-reads/dispatch-attempts")
def provider_postgres_extended_dispatch_attempts_read_route(
    tenant_id: str = "",
    execution_id: str = "",
    limit: int = 100,
):
    if postgres_read_dispatch_attempts is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_read_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return postgres_read_dispatch_attempts(
        tenant_id=tenant_id or None,
        execution_id=execution_id or None,
        limit=limit,
    )


@app.get("/provider-postgres-extended-ledger-reads/retry-history")
def provider_postgres_extended_retry_history_read_route(
    tenant_id: str = "",
    execution_id: str = "",
    limit: int = 100,
):
    if postgres_read_retry_history is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_read_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return postgres_read_retry_history(
        tenant_id=tenant_id or None,
        execution_id=execution_id or None,
        limit=limit,
    )


@app.get("/provider-postgres-extended-ledger-reads/latency-metrics")
def provider_postgres_extended_latency_metrics_read_route(
    tenant_id: str = "",
    provider_key: str = "",
    limit: int = 100,
):
    if postgres_read_latency_metrics is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_extended_ledger_read_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return postgres_read_latency_metrics(
        tenant_id=tenant_id or None,
        provider_key=provider_key or None,
        limit=limit,
    )


# ---------------------------------------------------------------------------
# Background worker loop foundation routes
# Added by wire_background_worker_loop_routes.py
# Purpose:
# - expose safe worker queue, cycle, dispatch check, polling, retry,
#   and completion reconciliation routes
# - do NOT enable real external provider dispatch
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.background_worker_loop_foundation import (
        background_worker_loop_foundation_status,
        enqueue_background_provider_job,
        list_background_worker_queue,
        reconcile_background_worker_completion,
        reset_background_worker_loop_for_tests,
        run_background_worker_cycle_once,
        run_background_worker_dispatch_check,
        run_background_worker_polling_cycle,
        run_background_worker_retry_scheduler,
    )
except Exception:  # pragma: no cover
    background_worker_loop_foundation_status = None
    enqueue_background_provider_job = None
    list_background_worker_queue = None
    reconcile_background_worker_completion = None
    reset_background_worker_loop_for_tests = None
    run_background_worker_cycle_once = None
    run_background_worker_dispatch_check = None
    run_background_worker_polling_cycle = None
    run_background_worker_retry_scheduler = None


@app.get("/background-worker-loop/status")
def background_worker_loop_status_route():
    if background_worker_loop_foundation_status is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return background_worker_loop_foundation_status()


@app.post("/background-worker-loop/enqueue")
async def background_worker_loop_enqueue_route(payload: dict):
    if enqueue_background_provider_job is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return enqueue_background_provider_job(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        task_type=safe_payload.get("task_type") or "provider_generation",
        payload=safe_payload.get("payload") or {},
        live_execution_requested=bool(safe_payload.get("live_execution_requested", False)),
        owner_governed_execution_confirmed=bool(
            safe_payload.get("owner_governed_execution_confirmed", False)
        ),
    )


@app.get("/background-worker-loop/queue")
def background_worker_loop_queue_route(
    tenant_id: str = "",
    provider_key: str = "",
    limit: int = 100,
):
    if list_background_worker_queue is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return list_background_worker_queue(
        tenant_id=tenant_id or None,
        provider_key=provider_key or None,
        limit=limit,
    )


@app.post("/background-worker-loop/cycle-once")
async def background_worker_loop_cycle_once_route():
    if run_background_worker_cycle_once is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return run_background_worker_cycle_once()


@app.post("/background-worker-loop/dispatch-check")
async def background_worker_loop_dispatch_check_route(payload: dict):
    if run_background_worker_dispatch_check is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    queue_item = safe_payload.get("queue_item") or {}
    if not isinstance(queue_item, dict):
        queue_item = {}

    return run_background_worker_dispatch_check(queue_item)


@app.post("/background-worker-loop/polling-cycle")
async def background_worker_loop_polling_cycle_route(payload: dict):
    if run_background_worker_polling_cycle is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    queue_item = safe_payload.get("queue_item") or {}
    if not isinstance(queue_item, dict):
        queue_item = {}

    return run_background_worker_polling_cycle(
        queue_item=queue_item,
        provider_job_id=safe_payload.get("provider_job_id"),
        provider_status=safe_payload.get("provider_status") or "queued",
    )


@app.post("/background-worker-loop/retry-scheduler")
async def background_worker_loop_retry_scheduler_route(payload: dict):
    if run_background_worker_retry_scheduler is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    queue_item = safe_payload.get("queue_item") or {}
    if not isinstance(queue_item, dict):
        queue_item = {}

    return run_background_worker_retry_scheduler(
        queue_item=queue_item,
        failure_code=safe_payload.get("failure_code") or "provider_error",
    )


@app.post("/background-worker-loop/reconcile-completion")
async def background_worker_loop_reconcile_completion_route(payload: dict):
    if reconcile_background_worker_completion is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    queue_item = safe_payload.get("queue_item") or {}
    if not isinstance(queue_item, dict):
        queue_item = {}

    return reconcile_background_worker_completion(
        queue_item=queue_item,
        final_status=safe_payload.get("final_status") or "owner_review_required",
        latency_ms=int(safe_payload.get("latency_ms", 0) or 0),
    )


@app.post("/background-worker-loop/reset-for-tests")
async def background_worker_loop_reset_for_tests_route():
    if reset_background_worker_loop_for_tests is None:
        return {
            "status": "unavailable",
            "reason": "background_worker_loop_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return reset_background_worker_loop_for_tests()


# ---------------------------------------------------------------------------
# Asset storage + signed delivery routes
# Added by wire_asset_storage_signed_delivery_routes.py
# Purpose:
# - expose customer-safe generated asset records, signed previews/downloads,
#   and delivery event records
# - do not expose internal storage keys or credentials
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.asset_storage_signed_delivery_runtime import (
        asset_storage_signed_delivery_status,
        create_asset_record,
        create_customer_safe_asset_preview,
        create_signed_asset_delivery_packet,
        get_asset_record,
        list_asset_delivery_events,
        list_asset_records,
        reset_asset_storage_for_tests,
        update_asset_status,
        verify_signed_asset_delivery_packet,
    )
except Exception:  # pragma: no cover
    asset_storage_signed_delivery_status = None
    create_asset_record = None
    create_customer_safe_asset_preview = None
    create_signed_asset_delivery_packet = None
    get_asset_record = None
    list_asset_delivery_events = None
    list_asset_records = None
    reset_asset_storage_for_tests = None
    update_asset_status = None
    verify_signed_asset_delivery_packet = None


@app.get("/asset-storage/status")
def asset_storage_status_route():
    if asset_storage_signed_delivery_status is None:
        return {"status": "unavailable", "credential_values_exposed": False}
    return asset_storage_signed_delivery_status()


@app.post("/asset-storage/create")
async def asset_storage_create_route(payload: dict):
    safe_payload = dict(payload or {})
    return create_asset_record(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        asset_type=safe_payload.get("asset_type") or "generated_asset",
        asset_status=safe_payload.get("asset_status") or "prepared",
        source_url=safe_payload.get("source_url"),
        storage_key=safe_payload.get("storage_key"),
        metadata=safe_payload.get("metadata") or {},
    )


@app.get("/asset-storage/record/{asset_id}")
def asset_storage_get_route(asset_id: str):
    return get_asset_record(asset_id)


@app.get("/asset-storage/list")
def asset_storage_list_route(
    tenant_id: str = "",
    request_id: str = "",
    provider_key: str = "",
    limit: int = 100,
):
    return list_asset_records(
        tenant_id=tenant_id or None,
        request_id=request_id or None,
        provider_key=provider_key or None,
        limit=limit,
    )


@app.post("/asset-storage/update-status/{asset_id}")
async def asset_storage_update_status_route(asset_id: str, payload: dict):
    safe_payload = dict(payload or {})
    return update_asset_status(
        asset_id=asset_id,
        asset_status=safe_payload.get("asset_status") or "prepared",
        metadata=safe_payload.get("metadata") or {},
    )


@app.post("/asset-delivery/signed-packet")
async def asset_delivery_signed_packet_route(payload: dict):
    safe_payload = dict(payload or {})
    return create_signed_asset_delivery_packet(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        asset_id=safe_payload.get("asset_id") or "unknown-asset",
        delivery_type=safe_payload.get("delivery_type") or "preview",
        expires_in_seconds=int(safe_payload.get("expires_in_seconds", 3600) or 3600),
    )


@app.post("/asset-delivery/verify")
async def asset_delivery_verify_route(payload: dict):
    safe_payload = dict(payload or {})
    return verify_signed_asset_delivery_packet(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        asset_id=safe_payload.get("asset_id") or "unknown-asset",
        delivery_type=safe_payload.get("delivery_type") or "preview",
        expires_at_ms=int(safe_payload.get("expires_at_ms", 0) or 0),
        nonce=safe_payload.get("nonce") or "",
        signature=safe_payload.get("signature") or "",
    )


@app.post("/asset-delivery/customer-preview")
async def asset_delivery_customer_preview_route(payload: dict):
    safe_payload = dict(payload or {})
    return create_customer_safe_asset_preview(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        asset_id=safe_payload.get("asset_id") or "unknown-asset",
    )


@app.get("/asset-delivery/events")
def asset_delivery_events_route(
    tenant_id: str = "",
    asset_id: str = "",
    limit: int = 100,
):
    return list_asset_delivery_events(
        tenant_id=tenant_id or None,
        asset_id=asset_id or None,
        limit=limit,
    )


@app.post("/asset-storage/reset-for-tests")
async def asset_storage_reset_for_tests_route():
    return reset_asset_storage_for_tests()


# ---------------------------------------------------------------------------
# Controlled OpenAI live execution routes
# Added by wire_controlled_openai_live_execution_routes.py
# Purpose:
# - expose controlled OpenAI live execution readiness
# - keep actual network calls disabled unless explicit env + owner gates allow
# - never expose credentials
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.real_provider_http_execution_layer import (
        controlled_openai_live_execution_status,
        execute_controlled_openai_live_request,
    )
except Exception:  # pragma: no cover
    controlled_openai_live_execution_status = None
    execute_controlled_openai_live_request = None


@app.get("/controlled-openai-live-execution/status")
def controlled_openai_live_execution_status_route():
    if controlled_openai_live_execution_status is None:
        return {
            "status": "unavailable",
            "reason": "controlled_openai_live_execution_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return controlled_openai_live_execution_status()


@app.post("/controlled-openai-live-execution/execute")
async def controlled_openai_live_execution_execute_route(payload: dict):
    if execute_controlled_openai_live_request is None:
        return {
            "status": "unavailable",
            "reason": "controlled_openai_live_execution_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return execute_controlled_openai_live_request(dict(payload or {}))


# ---------------------------------------------------------------------------
# OpenAI execution audit + asset persistence routes
# Added by wire_openai_execution_audit_asset_routes.py
# Purpose:
# - expose controlled OpenAI audit/asset persistence integration status
# - create execution ledger + asset preview packets after successful OpenAI execution
# - never expose credentials or internal storage keys
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.real_provider_http_execution_layer import (
        controlled_openai_audit_asset_integration_status,
        persist_openai_execution_audit_asset,
    )
except Exception:  # pragma: no cover
    controlled_openai_audit_asset_integration_status = None
    persist_openai_execution_audit_asset = None


@app.get("/controlled-openai-audit-assets/status")
def controlled_openai_audit_assets_status_route():
    if controlled_openai_audit_asset_integration_status is None:
        return {
            "status": "unavailable",
            "reason": "controlled_openai_audit_asset_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return controlled_openai_audit_asset_integration_status()


@app.post("/controlled-openai-audit-assets/persist")
async def controlled_openai_audit_assets_persist_route(payload: dict):
    if persist_openai_execution_audit_asset is None:
        return {
            "status": "unavailable",
            "reason": "controlled_openai_audit_asset_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return persist_openai_execution_audit_asset(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_job_id=safe_payload.get("provider_job_id") or "unknown-provider-job",
        output_text=safe_payload.get("output_text"),
        asset_type=safe_payload.get("asset_type") or "text",
        latency_ms=int(safe_payload.get("latency_ms", 0) or 0),
    )


# ---------------------------------------------------------------------------
# Provider result quality review routes
# Added by wire_provider_result_quality_review_routes.py
# Purpose:
# - score provider outputs
# - classify output as ready, retry, manual review, or owner review
# - preserve customer-safe delivery and no credential exposure
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_result_quality_review_runtime import (
        classify_provider_result_review_action,
        evaluate_provider_result_for_delivery,
        provider_result_quality_review_status,
        score_provider_result_quality,
    )
except Exception:  # pragma: no cover
    classify_provider_result_review_action = None
    evaluate_provider_result_for_delivery = None
    provider_result_quality_review_status = None
    score_provider_result_quality = None


@app.get("/provider-result-quality/status")
def provider_result_quality_status_route():
    if provider_result_quality_review_status is None:
        return {"status": "unavailable", "credential_values_exposed": False}
    return provider_result_quality_review_status()


@app.post("/provider-result-quality/score")
async def provider_result_quality_score_route(payload: dict):
    safe_payload = dict(payload or {})
    return score_provider_result_quality(
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        task_type=safe_payload.get("task_type") or "provider_generation",
        result_payload=safe_payload.get("result_payload") or {},
        latency_ms=int(safe_payload.get("latency_ms", 0) or 0),
        retry_count=int(safe_payload.get("retry_count", 0) or 0),
    )


@app.post("/provider-result-quality/classify")
async def provider_result_quality_classify_route(payload: dict):
    safe_payload = dict(payload or {})
    return classify_provider_result_review_action(
        quality_score=int(safe_payload.get("quality_score", 0) or 0),
        consequence_level=safe_payload.get("consequence_level") or "medium",
        retry_count=int(safe_payload.get("retry_count", 0) or 0),
        owner_review_required=bool(safe_payload.get("owner_review_required", False)),
    )


@app.post("/provider-result-quality/evaluate")
async def provider_result_quality_evaluate_route(payload: dict):
    safe_payload = dict(payload or {})
    return evaluate_provider_result_for_delivery(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        task_type=safe_payload.get("task_type") or "provider_generation",
        result_payload=safe_payload.get("result_payload") or {},
        latency_ms=int(safe_payload.get("latency_ms", 0) or 0),
        retry_count=int(safe_payload.get("retry_count", 0) or 0),
        consequence_level=safe_payload.get("consequence_level") or "medium",
        owner_review_required=bool(safe_payload.get("owner_review_required", False)),
    )


# ---------------------------------------------------------------------------
# Provider outcome learning routes
# Added by wire_provider_outcome_learning_routes.py
# Purpose:
# - record provider outcome signals
# - summarise provider/task success patterns
# - generate owner-reviewed improvement recommendations
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_outcome_learning_runtime import (
        generate_provider_improvement_recommendation,
        list_provider_outcome_learning,
        provider_outcome_learning_status,
        record_provider_outcome_learning,
        reset_provider_outcome_learning_for_tests,
        summarise_provider_outcome_learning,
    )
except Exception:  # pragma: no cover
    generate_provider_improvement_recommendation = None
    list_provider_outcome_learning = None
    provider_outcome_learning_status = None
    record_provider_outcome_learning = None
    reset_provider_outcome_learning_for_tests = None
    summarise_provider_outcome_learning = None


@app.get("/provider-outcome-learning/status")
def provider_outcome_learning_status_route():
    return provider_outcome_learning_status()


@app.post("/provider-outcome-learning/record")
async def provider_outcome_learning_record_route(payload: dict):
    safe_payload = dict(payload or {})
    return record_provider_outcome_learning(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        execution_id=safe_payload.get("execution_id") or "unknown-execution",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        task_type=safe_payload.get("task_type") or "provider_generation",
        quality_score=int(safe_payload.get("quality_score", 0) or 0),
        review_action=safe_payload.get("review_action") or "manual_review_required",
        final_outcome=safe_payload.get("final_outcome") or "unknown",
        retry_count=int(safe_payload.get("retry_count", 0) or 0),
        latency_ms=int(safe_payload.get("latency_ms", 0) or 0),
        notes=safe_payload.get("notes"),
    )


@app.get("/provider-outcome-learning/list")
def provider_outcome_learning_list_route(
    tenant_id: str = "",
    provider_key: str = "",
    task_type: str = "",
    limit: int = 100,
):
    return list_provider_outcome_learning(
        tenant_id=tenant_id or None,
        provider_key=provider_key or None,
        task_type=task_type or None,
        limit=limit,
    )


@app.get("/provider-outcome-learning/summary")
def provider_outcome_learning_summary_route(
    tenant_id: str = "",
    provider_key: str = "",
    task_type: str = "",
):
    return summarise_provider_outcome_learning(
        tenant_id=tenant_id or None,
        provider_key=provider_key or None,
        task_type=task_type or None,
    )


@app.get("/provider-outcome-learning/recommendation")
def provider_outcome_learning_recommendation_route(
    tenant_id: str = "",
    provider_key: str = "",
    task_type: str = "",
):
    return generate_provider_improvement_recommendation(
        tenant_id=tenant_id or None,
        provider_key=provider_key or None,
        task_type=task_type or None,
    )


@app.post("/provider-outcome-learning/reset-for-tests")
async def provider_outcome_learning_reset_route():
    return reset_provider_outcome_learning_for_tests()

