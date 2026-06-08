from __future__ import annotations

import time
import uuid
from typing import Dict, Any, List

from backend.app.runtime.autonomous_governed_action_router import (
    route_autonomous_governed_packet,
)
from backend.app.runtime.persistent_action_execution_history import (
    record_action_execution,
)
from backend.app.runtime.intelligent_action_packet_normalizer import (
    normalize_implementation_plan,
)
from backend.app.runtime.durable_external_action_records import (
    record_external_actions,
)
from backend.app.runtime.durable_orchestration_state_runtime import (
    create_orchestration_plan,
    create_orchestration_step,
    create_recovery_checkpoint,
    record_orchestration_event,
    record_orchestration_result_memory,
    update_orchestration_plan_status,
    update_orchestration_step_status,
)
from backend.app.runtime.durable_manual_review_recovery_runtime import (
    create_manual_review_item,
    create_recovery_action,
)


def _now_ms() -> int:
    return int(time.time() * 1000)


SPECIALIST_OUTPUTS = {
    "security_compliance_agent": {
        "deliverable_type": "compliance_framework",
        "completed_output": "Generated HIPAA/GDPR compliance readiness framework with governance checkpoints and audit review schedule."
    },
    "analytics_optimisation_agent": {
        "deliverable_type": "analytics_dashboard_plan",
        "completed_output": "Prepared KPI dashboard structure covering pipeline conversion, pilot engagement tracking, and healthcare sector growth metrics."
    },
    "lead_generator_appointment_setter_agent": {
        "deliverable_type": "lead_generation_campaign",
        "completed_output": "Prepared healthcare outreach targeting framework including pilot-client acquisition strategy and appointment funnel."
    },
    "business_growth_partnerships_agent": {
        "deliverable_type": "partnership_strategy",
        "completed_output": "Generated healthcare partnership and alliance roadmap targeting healthcare technology vendors and innovation hubs."
    },
    "social_media_manager_content_creator_agent": {
        "deliverable_type": "thought_leadership_content",
        "completed_output": "Generated webinar and thought-leadership rollout strategy for healthcare technology positioning."
    },
    "website_landing_apps_agent": {
        "deliverable_type": "digital_experience_plan",
        "completed_output": "Prepared healthcare-focused landing page and digital experience implementation outline."
    },
    "crm_ai_agent": {
        "deliverable_type": "crm_pipeline_setup",
        "completed_output": "Generated CRM nurture and healthcare pipeline automation recommendations."
    },
    "seo_agent": {
        "deliverable_type": "seo_strategy",
        "completed_output": "Prepared healthcare SEO topic cluster and organic growth strategy."
    },
    "marketing_specialist_agent": {
        "deliverable_type": "marketing_execution",
        "completed_output": "Generated healthcare market positioning and campaign execution recommendations."
    },
    "orchestration_agent": {
        "deliverable_type": "workflow_coordination",
        "completed_output": "Prepared orchestration workflow coordination and execution review structure."
    }
}

CREATIVE_MEDIA_TASK_KEYWORDS = {
    "creative media",
    "media asset",
    "video",
    "image",
    "avatar",
    "ugc",
    "ad creative",
    "product photo",
    "product image",
    "visual",
    "audio",
    "voiceover",
}


def _creative_media_agent_ids() -> set[str]:
    try:
        from backend.app.runtime.shared_creative_media_generation_runtime import CREATIVE_MEDIA_AGENTS

        return set(CREATIVE_MEDIA_AGENTS)
    except Exception:
        return {
            "ugc_creative_agent",
            "paid_ads_agent",
            "product_image_agent",
            "social_media_manager_content_creator_agent",
            "brand_strategy_agent",
            "marketing_specialist_agent",
            "website_landing_apps_agent",
            "creative_rotation_agent",
        }


def _packet_action_text(packet: Dict[str, Any], fallback: str = "") -> str:
    return str(
        packet.get("user_requested_task")
        or packet.get("implementation_action")
        or packet.get("action")
        or packet.get("title")
        or packet.get("description")
        or fallback
        or "Create a premium customer-safe creative media asset."
    )


def _is_creative_media_packet(packet: Dict[str, Any], assigned_agent: str) -> bool:
    agent_id = str(assigned_agent or "").strip()
    if agent_id in _creative_media_agent_ids():
        return True

    haystack = " ".join(
        [
            agent_id,
            str(packet.get("implementation_action") or ""),
            str(packet.get("action") or ""),
            str(packet.get("title") or ""),
            str(packet.get("description") or ""),
            str(packet.get("deliverable_type") or ""),
        ]
    ).lower().replace("_", " ")
    return any(keyword in haystack for keyword in CREATIVE_MEDIA_TASK_KEYWORDS)


def _enqueue_canonical_creative_media_job(
    *,
    packet: Dict[str, Any],
    packet_result: Dict[str, Any],
    assigned_agent: str,
    tenant_id: str,
) -> Dict[str, Any]:
    if not _is_creative_media_packet(packet, assigned_agent):
        return {
            "canonical_job_attempted": False,
            "canonical_job_created": False,
            "canonical_job_id": None,
            "canonical_store": "backend:runtime_outputs/media_jobs",
            "status": "not_creative_media_packet",
            "credential_values_exposed": False,
        }

    existing_job_id = str(
        packet.get("existing_media_job_id")
        or packet.get("canonical_job_id")
        or packet.get("media_job_id")
        or packet.get("job_id")
        or ""
    ).strip()

    if existing_job_id:
        try:
            from backend.app.runtime.async_media_job_foundation import media_job_store_context, read_media_job

            existing_job = read_media_job(existing_job_id)
            context = media_job_store_context()
            return {
                "canonical_job_attempted": True,
                "canonical_job_created": False,
                "canonical_job_id": existing_job_id,
                "canonical_store": context.get("canonical_store", "backend:runtime_outputs/media_jobs"),
                "media_job_status": existing_job.get("status", "unknown"),
                "status": "existing_canonical_media_job_linked" if existing_job.get("success") is not False else "existing_canonical_media_job_not_found",
                "credential_values_exposed": False,
            }
        except Exception as exc:
            return {
                "canonical_job_attempted": True,
                "canonical_job_created": False,
                "canonical_job_id": existing_job_id,
                "canonical_store": "backend:runtime_outputs/media_jobs",
                "status": "existing_canonical_media_job_lookup_failed",
                "error": str(exc)[:260],
                "credential_values_exposed": False,
            }

    try:
        from backend.app.runtime.async_media_job_foundation import media_job_store_context

        context = media_job_store_context()
        return {
            "canonical_job_attempted": False,
            "canonical_job_created": False,
            "canonical_job_id": None,
            "canonical_store": context.get("canonical_store", "backend:runtime_outputs/media_jobs"),
            "media_job_status": "missing_existing_media_job_id",
            "status": "missing_existing_media_job_id",
            "credential_values_exposed": False,
        }
    except Exception as exc:
        return {
            "canonical_job_attempted": False,
            "canonical_job_created": False,
            "canonical_job_id": None,
            "canonical_store": "backend:runtime_outputs/media_jobs",
            "status": "canonical_media_job_context_unavailable",
            "error": str(exc)[:260],
            "credential_values_exposed": False,
        }


def execute_delegated_workforce_plan(
    *,
    implementation_plan: Dict[str, Any],
    owner_approved: bool = False,
    client_owned_agents: List[str] | None = None,
    package_tier: str = "starter",
    connected_integrations: List[str] | None = None,
    tenant_id: str = "owner_admin",
    media_job_processing_authorized: bool = False,
) -> Dict[str, Any]:

    client_owned_agents = client_owned_agents or []
    connected_integrations = connected_integrations or []

    implementation_plan = normalize_implementation_plan(
        implementation_plan or {"action_packets": []},
        fallback_agent="marketing_specialist_agent",
    )

    package_tier = (package_tier or "starter").lower()

    enterprise_access = package_tier == "enterprise"
    execution_id = f"delegated_exec_{uuid.uuid4().hex[:12]}"
    orchestration_id = str(
        implementation_plan.get("orchestration_id")
        or implementation_plan.get("plan_id")
        or execution_id
    )

    plan_persistence = create_orchestration_plan(
        orchestration_id=orchestration_id,
        tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
        project_id=str(implementation_plan.get("project_id") or orchestration_id),
        root_agent_id=str(implementation_plan.get("lead_agent") or "orchestration_agent"),
        status="in_progress",
        plan_type="delegated_workforce_execution",
        payload={
            "normalization": implementation_plan.get("normalization"),
            "packet_count": len(implementation_plan.get("action_packets", [])),
            "package_tier": package_tier,
            "connected_integrations": connected_integrations,
            "execution_id": execution_id,
        },
    )
    if not plan_persistence.get("success"):
        return plan_persistence

    execution_results = []
    queued_results = []
    blocked_results = []

    def _record_review_link(
        *,
        packet_id: str,
        assigned_agent: str,
        status: str,
        reason: str,
        packet: Dict[str, Any],
        review_type: str = "delegated_workforce_review",
        priority: str = "medium",
    ) -> Dict[str, Any]:
        review = create_manual_review_item(
            tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
            project_id=str(implementation_plan.get("project_id") or orchestration_id),
            source_type="delegated_workforce_execution",
            source_id=f"{orchestration_id}:{packet_id}:{status}",
            orchestration_id=orchestration_id,
            orchestration_step_id=packet_id,
            packet_id=packet_id,
            execution_id=execution_id,
            review_type=review_type,
            status=status,
            priority=priority,
            reason=reason,
            summary="Delegated workforce execution requires owner/admin review before recovery.",
            payload={"packet": packet, "assigned_agent": assigned_agent},
        )
        if review.get("success"):
            create_recovery_action(
                tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
                project_id=str(implementation_plan.get("project_id") or orchestration_id),
                review_id=str(review.get("review_id") or ""),
                orchestration_id=orchestration_id,
                action_type=status,
                status="requested",
                payload={"packet_id": packet_id, "reason": reason, "assigned_agent": assigned_agent},
            )
        return review

    previous_step_id = None
    for packet in implementation_plan.get("action_packets", []):

        assigned_agent = packet.get("recommended_agent", "orchestration_agent")
        packet_id = str(packet.get("packet_id") or f"{orchestration_id}_packet_{len(execution_results) + len(queued_results) + len(blocked_results) + 1:03d}")
        step_created = create_orchestration_step(
            step_id=packet_id,
            orchestration_id=orchestration_id,
            tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
            agent_id=assigned_agent,
            action_type=str(packet.get("implementation_action") or packet.get("title") or "delegated_workforce_action"),
            status="prepared",
            dependency_step_ids=[previous_step_id] if previous_step_id else [],
        )
        if not step_created.get("success"):
            return step_created
        previous_step_id = packet_id

        agent_owned = (
            enterprise_access
            or assigned_agent in client_owned_agents
        )

        specialist = SPECIALIST_OUTPUTS.get(
            assigned_agent,
            SPECIALIST_OUTPUTS["orchestration_agent"]
        )

        packet_result = {
            "packet_id": packet_id,
            "orchestration_id": orchestration_id,
            "execution_id": execution_id,
            "assigned_agent": assigned_agent,
            "deliverable_type": specialist["deliverable_type"],
            "risk_level": packet.get("risk_level", "medium"),
            "customer_safe": True,
            "created_at_ms": _now_ms(),
        }

        if not agent_owned:
            packet_result.update({
                "execution_status": "agent_not_owned",
                "delegate_execution": "blocked",
                "recommendation_visibility": True,
                "upsell_visibility": True,
                "execution_preview": "allowed",
                "completed_output": None,
                "upgrade_recommendation": assigned_agent,
                "autonomous_governance": True,
                "autonomous_route": "recommendation_only",
                "performed_actual_action": False,
                "real_execution": False,
            })
            update_orchestration_step_status(
                step_id=packet_id,
                orchestration_id=orchestration_id,
                tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
                status="blocked_agent_not_owned",
            )
            record_orchestration_event(
                orchestration_id=orchestration_id,
                step_id=packet_id,
                tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
                event_type="delegated_packet_blocked",
                payload={"reason": "agent_not_owned", "assigned_agent": assigned_agent},
            )
            review = _record_review_link(
                packet_id=packet_id,
                assigned_agent=assigned_agent,
                status="manual_review_required",
                reason="agent_not_owned",
                packet=packet,
                review_type="delegated_agent_not_owned",
            )
            packet_result["review_item"] = review.get("item")
            blocked_results.append(packet_result)
            continue

        if packet.get("approval_required") and not owner_approved:
            packet_result.update({
                "execution_status": "awaiting_owner_approval",
                "delegate_execution": "blocked",
                "completed_output": None,
            })
            update_orchestration_step_status(
                step_id=packet_id,
                orchestration_id=orchestration_id,
                tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
                status="queued_for_owner_approval",
            )
            create_recovery_checkpoint(
                orchestration_id=orchestration_id,
                tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
                checkpoint_type="owner_approval_queue",
                recoverable_status="queued_for_owner_approval",
                payload={"packet_id": packet_id, "assigned_agent": assigned_agent},
            )
            review = _record_review_link(
                packet_id=packet_id,
                assigned_agent=assigned_agent,
                status="queued_for_owner_approval",
                reason="owner_approval_required_for_delegated_packet",
                packet=packet,
                review_type="owner_approval",
                priority="high",
            )
            packet_result["review_item"] = review.get("item")
            queued_results.append(packet_result)
            continue

        autonomous_route_result = route_autonomous_governed_packet(
            {
                "packet_id": packet_id,
                "step_id": packet_id,
                "orchestration_id": orchestration_id,
                "assigned_agent": assigned_agent,
                "recommended_agent": assigned_agent,
                "implementation_action": (
                    packet.get("implementation_action")
                    or packet.get("title")
                    or specialist["completed_output"]
                ),
                "risk_level": packet.get("risk_level", "medium"),
            },
            package_tier=package_tier,
            client_owned_agents=client_owned_agents,
            actor_role="owner_admin" if enterprise_access else "client",
            tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
            owner_approved=owner_approved,
            connected_integrations=connected_integrations,
        )
        if not autonomous_route_result.get("success", False):
            return autonomous_route_result

        packet_result.update({
            "execution_status": autonomous_route_result.get("routing_status"),
            "delegate_execution": (
                "executed"
                if autonomous_route_result.get("performed_actual_action")
                else "blocked"
            ),
            "performed_actual_action": autonomous_route_result.get("performed_actual_action", False),
            "autonomous_governance": True,
            "autonomous_route": autonomous_route_result.get("routing_status"),
            "governance": autonomous_route_result.get("governance"),
            "real_execution": True,
            "deliverable": autonomous_route_result.get("deliverable"),
            "completed_output": (
                autonomous_route_result.get("deliverable", {})
                .get("content", {})
                .get("body")
            ),
            "external_action_performed": (
                autonomous_route_result.get("execution", {})
                .get("external_provider_called", False)
            ),
            "live_external_call_executed": (
                autonomous_route_result.get("execution", {})
                .get("external_provider_called", False)
            ),
        })

        if autonomous_route_result.get("routing_status") in {
            "queued_for_owner_approval",
            "manual_review_required",
        }:
            update_orchestration_step_status(
                step_id=packet_id,
                orchestration_id=orchestration_id,
                tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
                status=str(autonomous_route_result.get("routing_status")),
            )
            create_recovery_checkpoint(
                orchestration_id=orchestration_id,
                tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
                checkpoint_type=str(autonomous_route_result.get("routing_status")),
                recoverable_status=str(autonomous_route_result.get("routing_status")),
                payload={
                    "packet_id": packet_id,
                    "assigned_agent": assigned_agent,
                    "review_id": (autonomous_route_result.get("review_item") or {}).get("review_id"),
                },
            )
            packet_result["review_item"] = autonomous_route_result.get("review_item")
            create_recovery_action(
                tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
                project_id=str(implementation_plan.get("project_id") or orchestration_id),
                review_id=str((autonomous_route_result.get("review_item") or {}).get("review_id") or ""),
                orchestration_id=orchestration_id,
                action_type=str(autonomous_route_result.get("routing_status")),
                status="requested",
                payload={"packet_id": packet_id, "assigned_agent": assigned_agent},
            )
            queued_results.append(packet_result)
        elif autonomous_route_result.get("routing_status") == "recommendation_only":
            update_orchestration_step_status(
                step_id=packet_id,
                orchestration_id=orchestration_id,
                tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
                status="recommendation_only",
            )
            blocked_results.append(packet_result)
        else:
            update_orchestration_step_status(
                step_id=packet_id,
                orchestration_id=orchestration_id,
                tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
                status="completed",
            )
            record_orchestration_result_memory(
                orchestration_id=orchestration_id,
                step_id=packet_id,
                tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
                agent_id=assigned_agent,
                result_type="delegated_workforce_packet_result",
                result_summary=str(packet_result.get("completed_output") or packet_result.get("execution_status") or "")[:500],
                payload=packet_result,
            )
            history_record = record_action_execution(
                tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
                packet_id=packet_result.get("packet_id"),
                assigned_agent=assigned_agent,
                execution_payload=packet_result,
            )
            packet_result["history_id"] = history_record.get("history_id")
            packet_result["history_persisted"] = True

            external_records = record_external_actions(
                tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
                execution_id=packet_result.get("execution_id"),
                packet_id=packet_result.get("packet_id"),
                assigned_agent=assigned_agent,
                deliverable=packet_result.get("deliverable"),
            )
            packet_result["external_action_record_count"] = external_records.get("record_count", 0)
            packet_result["external_action_records_persisted"] = external_records.get("record_count", 0) > 0
            packet_result["external_action_records"] = external_records.get("records", [])

            canonical_media_job = _enqueue_canonical_creative_media_job(
                packet=packet,
                packet_result=packet_result,
                assigned_agent=assigned_agent,
                tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
            )
            packet_result.update({
                "canonical_job_attempted": bool(canonical_media_job.get("canonical_job_attempted")),
                "canonical_job_created": bool(canonical_media_job.get("canonical_job_created")),
                "canonical_job_id": canonical_media_job.get("canonical_job_id"),
                "canonical_store": canonical_media_job.get("canonical_store", "backend:runtime_outputs/media_jobs"),
                "media_job_created": bool(canonical_media_job.get("canonical_job_created")),
                "media_job_id": canonical_media_job.get("canonical_job_id"),
            })

            execution_results.append(packet_result)

    final_status = "completed" if execution_results and not queued_results and not blocked_results else "requires_review"
    if not execution_results and blocked_results and not queued_results:
        final_status = "blocked"
    update_orchestration_plan_status(
        orchestration_id=orchestration_id,
        status=final_status,
        completed=final_status == "completed",
        failed=final_status == "blocked",
    )
    record_orchestration_event(
        orchestration_id=orchestration_id,
        tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
        event_type="delegated_workforce_execution_finished",
        payload={
            "completed_count": len(execution_results),
            "queued_count": len(queued_results),
            "blocked_count": len(blocked_results),
            "status": final_status,
        },
    )

    if media_job_processing_authorized:
        try:
            from backend.app.runtime.async_media_job_foundation import process_queued_creative_media_jobs

            media_job_runner = process_queued_creative_media_jobs(limit=25)
        except Exception as exc:
            media_job_runner = {
                "success": False,
                "status": "unavailable",
                "processed_count": 0,
                "results": [],
                "error": str(exc)[:500],
                "customer_safe": True,
                "credential_values_exposed": False,
            }
    else:
        media_job_runner = {
            "success": True,
            "status": "not_authorized",
            "processed_count": 0,
            "results": [],
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    canonical_jobs = [
        result
        for result in execution_results
        if result.get("canonical_job_id")
    ]

    return {
        "success": True,
        "profile": "delegated_workforce_execution_runtime_v1",
        "normalization": implementation_plan.get("normalization"),
        "execution_id": execution_id,
        "orchestration_id": orchestration_id,
        "completed_count": len(execution_results),
        "queued_count": len(queued_results),
        "blocked_count": len(blocked_results),
        "completed_results": execution_results,
        "queued_results": queued_results,
        "blocked_results": blocked_results,
        "canonical_job_attempted": any(result.get("canonical_job_attempted") is True for result in execution_results),
        "canonical_job_created": any(result.get("canonical_job_created") is True for result in canonical_jobs),
        "canonical_job_id": canonical_jobs[0].get("canonical_job_id") if canonical_jobs else None,
        "canonical_job_ids": [result.get("canonical_job_id") for result in canonical_jobs],
        "canonical_store": "backend:runtime_outputs/media_jobs",
        "media_job_processing_authorized": bool(media_job_processing_authorized),
        "media_job_runner_triggered": bool(media_job_processing_authorized and media_job_runner.get("success") is not False),
        "media_job_runner_status": media_job_runner.get("status", "unknown"),
        "media_job_processed_count": int(media_job_runner.get("processed_count") or 0),
        "media_job_runner_results": media_job_runner.get("results", []),
        "enterprise_access": enterprise_access,
        "connected_integrations": connected_integrations,
        "external_integration_count": len(connected_integrations),
        "customer_safe": True,
        "credential_values_exposed": False,
        "external_action_performed": False,
        "live_external_call_executed": False,
        "created_at_ms": _now_ms(),
    }
