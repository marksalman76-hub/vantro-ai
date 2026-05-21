from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from backend.app.core.durable_billing_state_store import apply_billing_runtime_mutation
from backend.app.core.stripe_tenant_mapping_store import resolve_tenant_by_stripe_ids


EVENT_MEMORY: list[Dict[str, Any]] = []


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def apply_stripe_classification_to_billing_runtime(
    event: Dict[str, Any],
    classification: Dict[str, Any],
) -> Dict[str, Any]:
    stripe_customer_id = event.get("stripe_customer_id")
    stripe_subscription_id = event.get("stripe_subscription_id")
    mapping_result = resolve_tenant_by_stripe_ids(
        stripe_customer_id=stripe_customer_id,
        stripe_subscription_id=stripe_subscription_id,
    )

    tenant_mapping = mapping_result.get("mapping") if mapping_result.get("resolved") else None
    tenant_id = tenant_mapping.get("tenant_id") if tenant_mapping else None
    action = classification.get("action")

    runtime_update = {
        "success": True,
        "tenant_id": tenant_id,
        "tenant_resolved": bool(tenant_id),
        "tenant_reference": tenant_id or f"unmapped_stripe_customer::{stripe_customer_id or 'unknown'}",
        "stripe_customer_id": stripe_customer_id,
        "stripe_subscription_id": stripe_subscription_id,
        "event_type": event.get("event_type"),
        "classification_action": action,
        "processed_at": utc_now_iso(),
        "durable_runtime_update_mode": "durable_state_mutation",
        "runtime_mutation_committed": False,
        "reason": "tenant_mapping_resolved" if tenant_id else "durable_tenant_stripe_mapping_pending",
        "mapping_match_type": mapping_result.get("match_type"),
    }

    if action == "mark_subscription_active_and_reset_monthly_credits":
        runtime_update.update({
            "target_subscription_status": "active",
            "target_client_execution_allowed": True,
            "target_credit_action": "reset_monthly_credits",
            "preserve_cycle_anchor": True,
        })

    elif action == "mark_subscription_past_due_and_block_client_credit_consuming_execution":
        runtime_update.update({
            "target_subscription_status": "past_due",
            "target_client_execution_allowed": False,
            "target_credit_action": "block_credit_consuming_execution",
            "retry_interval_hours": classification.get("retry_interval_hours", 48),
            "preserve_cycle_anchor": True,
        })

    elif action == "mark_subscription_cancelled_and_block_client_execution":
        runtime_update.update({
            "target_subscription_status": "cancelled",
            "target_client_execution_allowed": False,
            "target_credit_action": "block_client_execution",
            "preserve_cycle_anchor": True,
        })

    elif action == "sync_subscription_status_cancel_policy_and_cycle_dates":
        runtime_update.update({
            "target_subscription_status": event.get("status") or "sync_required",
            "target_client_execution_allowed": "depends_on_synced_subscription_status",
            "target_credit_action": "sync_only",
            "cancel_at_period_end": event.get("cancel_at_period_end"),
            "preserve_cycle_anchor": True,
        })

    else:
        runtime_update.update({
            "target_subscription_status": "unchanged",
            "target_client_execution_allowed": "unchanged",
            "target_credit_action": "none",
            "preserve_cycle_anchor": True,
        })

    if tenant_id:
        mutation = apply_billing_runtime_mutation(
            tenant_id=tenant_id,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            event_type=event.get("event_type"),
            target_subscription_status=runtime_update.get("target_subscription_status"),
            target_client_execution_allowed=runtime_update.get("target_client_execution_allowed"),
            target_credit_action=runtime_update.get("target_credit_action"),
            preserve_cycle_anchor=runtime_update.get("preserve_cycle_anchor", True),
            retry_interval_hours=runtime_update.get("retry_interval_hours"),
            cancel_at_period_end=runtime_update.get("cancel_at_period_end"),
        )
        runtime_update["runtime_mutation_committed"] = bool(mutation.get("mutation_committed"))
        runtime_update["durable_billing_mutation"] = mutation
    else:
        runtime_update["durable_billing_mutation"] = {
            "success": False,
            "mutation_committed": False,
            "reason": "tenant_not_resolved",
        }

    EVENT_MEMORY.append(runtime_update)
    return runtime_update


def latest_billing_bridge_events(limit: int = 20) -> Dict[str, Any]:
    return {
        "success": True,
        "count": len(EVENT_MEMORY[-limit:]),
        "events": EVENT_MEMORY[-limit:],
        "checked_at": utc_now_iso(),
    }
