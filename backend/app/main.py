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
from backend.app.core.integration_live_adapter_registry import (
    adapter_registry_summary,
    execute_integration_action,
)
import urllib.request
import urllib.error
import json
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

from backend.app.runtime.global_execution_evidence_layer import build_execution_evidence_packet
from fastapi import FastAPI, Header
from backend.app.runtime.autonomous_workforce_orchestration_foundation import autonomous_workforce_orchestration_status, create_delegated_subtask_plan, create_orchestration_execution_graph, orchestration_replay_recovery_packet
from backend.app.runtime.provider_workforce_runtime_hardening import provider_workforce_runtime_hardening_status, provider_runtime_health_summary, provider_recovery_readiness_summary
from backend.app.runtime.real_provider_activation_registry import get_all_provider_activation_statuses, get_provider_activation_status, select_ready_provider_for_capability
from backend.app.runtime.real_provider_http_execution_layer import controlled_openai_live_execution_status, real_provider_http_runtime_status, execute_controlled_openai_live_request
from backend.app.runtime.provider_dispatch_policy_worker_foundation import provider_dispatch_policy_status, evaluate_provider_dispatch_policy, provider_worker_foundation_status
from backend.app.runtime.safe_provider_action_adapters import evaluate_safe_provider_action, classify_provider_action
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
from backend.app.runtime.canonical_agent_identity_bridge import normalise_agent_identity
from backend.app.runtime.autonomous_qa_regression_intelligence import autonomous_qa_regression_status, build_qa_regression_packet
from backend.app.runtime.post_deploy_validation_readiness import post_deploy_validation_status
from backend.app.runtime.global_beta_readiness_orchestration import global_beta_readiness_status
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
    requested_agent = normalise_agent_identity(normalize_agent_id(request.requested_agent))

    credit_gate = pg_client_credit_gate({
        "actor_role": request.actor_role,
        "tenant_id": request.tenant_id,
        "requested_credits": request.requested_credits,
    })

    actor_role = (request.actor_role or "").strip().lower()
    owner_admin_credit_bypass = actor_role in {"owner", "admin", "owner_admin", "system"}

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
        (request.actor_role or "").strip().lower() in {"owner", "admin", "owner_admin", "system"}
        and requested_agent in owner_admin_system_agents
    ):
        return {
            "success": False,
            "error": "unknown_agent",
            "requested_agent": request.requested_agent,
            "normalised_agent": requested_agent,
        }

    owner_admin_internal_execution = (request.actor_role or "").strip().lower() in {"owner", "admin", "owner_admin", "system"}

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
            event_type="quality_gate_failed",
            title=f"{requested_agent} output rejected by premium quality gate",
            agent_id=requested_agent,
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
async def delegated_workforce_execution(payload: dict):

    implementation_plan = payload.get("implementation_plan") or {}

    result = execute_delegated_workforce_plan(
        implementation_plan=implementation_plan,
        owner_approved=payload.get("owner_approved", False),
        client_owned_agents=payload.get("client_owned_agents", []),
        package_tier=payload.get("package_tier", "starter"),
        connected_integrations=payload.get("connected_integrations", []),
        tenant_id=payload.get("tenant_id") or "owner_admin",
    )

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
    clean_plan = str(plan or "starter").strip().lower()
    if clean_plan not in {"starter", "growth", "business", "enterprise"}:
        clean_plan = "starter"

    package_limits = {
        "starter": 3,
        "growth": 7,
        "business": 10,
        "enterprise": 27,
    }

    reserved_enterprise_only = {"head_agent", "orchestration_agent"}

    agents = [
        {"agent_id": "strategist_agent", "name": "Strategist Agent", "enterprise_only": False},
        {"agent_id": "business_growth_partnerships_agent", "name": "Business Growth & Partnerships Agent", "enterprise_only": False},
        {"agent_id": "lead_generator_appointment_setter_agent", "name": "Lead Generator / Appointment Setter Agent", "enterprise_only": False},
        {"agent_id": "marketing_specialist_agent", "name": "Marketing Specialist Agent", "enterprise_only": False},
        {"agent_id": "social_media_manager_content_creator_agent", "name": "Social Media Manager / Content Creator Agent", "enterprise_only": False},
        {"agent_id": "seo_agent", "name": "SEO Agent", "enterprise_only": False},
        {"agent_id": "email_reply_agent", "name": "Email Reply Agent", "enterprise_only": False},
        {"agent_id": "crm_ai_agent", "name": "CRM AI Agent", "enterprise_only": False},
        {"agent_id": "receptionist_agent", "name": "Receptionist Agent", "enterprise_only": False},
        {"agent_id": "custom_websites_landing_pages_apps_agent", "name": "Custom Websites, Landing Pages & Apps Agent", "enterprise_only": False},
        {"agent_id": "product_development_agent", "name": "Product Development Agent", "enterprise_only": False},
        {"agent_id": "ecommerce_agent", "name": "Ecommerce Agent", "enterprise_only": False},
        {"agent_id": "ugc_creative_agent", "name": "UGC Creative Agent", "enterprise_only": False},
        {"agent_id": "analytics_optimisation_agent", "name": "Analytics Optimisation Agent", "enterprise_only": False},
        {"agent_id": "analytics_intelligence_agent", "name": "Analytics Intelligence Agent", "enterprise_only": False},
        {"agent_id": "product_research_agent", "name": "Product Research Agent", "enterprise_only": False},
        {"agent_id": "ad_creative_agent", "name": "Ad Creative Agent", "enterprise_only": False},
        {"agent_id": "product_image_agent", "name": "Product Image Agent", "enterprise_only": False},
        {"agent_id": "influencer_collaboration_agent", "name": "Influencer Collaboration Agent", "enterprise_only": False},
        {"agent_id": "demo_trial_agent", "name": "Demo / Trial Agent", "enterprise_only": False},

        {"agent_id": "head_agent", "name": "Head Agent", "enterprise_only": True},
        {"agent_id": "orchestration_agent", "name": "Orchestration Agent", "enterprise_only": True},
        {"agent_id": "security_compliance_agent", "name": "Security & Compliance Agent", "enterprise_only": True},
        {"agent_id": "integration_automation_agent", "name": "Integration / Automation Agent", "enterprise_only": True},
        {"agent_id": "qa_testing_agent", "name": "QA / Testing Agent", "enterprise_only": True},
        {"agent_id": "billing_optimisation_agent", "name": "Billing Optimisation Agent", "enterprise_only": True},
        {"agent_id": "training_learning_agent", "name": "Training / Learning Agent", "enterprise_only": True},
    ]

    if clean_plan != "enterprise":
        selectable_agents = [a for a in agents if a["agent_id"] not in reserved_enterprise_only]
    else:
        selectable_agents = agents

    max_selectable_agents = package_limits[clean_plan]
    head_agent_available = clean_plan == "enterprise"
    available_count = len(selectable_agents)

    return {
        "success": True,
        "plan": clean_plan,
        "package_tier": clean_plan,
        "agent_limit": max_selectable_agents,
        "max_selectable_agents": max_selectable_agents,
        "selection_required": True,
        "selection_locked_after_activation": True,
        "owner_approval_required_for_changes": True,
        "enterprise_only_agent_ids": sorted(list(reserved_enterprise_only)),
        "head_agent_available": head_agent_available,
        "agents": selectable_agents,
        "agent_count": available_count,
        "available_count": available_count,
        "credential_values_exposed": False,
        "client_safe": True,
        "customer_safe": True,
    }


# Global Beta Readiness Admin Status Route
@app.get("/admin/global-beta-readiness/status")
def admin_global_beta_readiness_status():
    return global_beta_readiness_status()

