from __future__ import annotations

from typing import Any, Dict, List

from backend.app.runtime.one_time_agent_selection_lock import (
    activate_agent_selection_once,
    create_agent_selection_draft,
    get_activated_agent_selection,
    request_post_activation_agent_change,
)


def create_signup_locked_selection_draft(
    *,
    tenant_id: str,
    package_id: str,
    plan: str,
    selected_agent_keys: List[str],
) -> Dict[str, Any]:
    return create_agent_selection_draft(
        tenant_id=tenant_id,
        package_id=package_id,
        plan=plan,
        selected_agent_keys=selected_agent_keys,
    )


def activate_signup_locked_selection(
    *,
    tenant_id: str,
    package_id: str,
    draft_id: str,
) -> Dict[str, Any]:
    return activate_agent_selection_once(
        tenant_id=tenant_id,
        package_id=package_id,
        draft_id=draft_id,
    )


def get_signup_locked_selection_status(
    *,
    tenant_id: str,
    package_id: str,
) -> Dict[str, Any]:
    return get_activated_agent_selection(
        tenant_id=tenant_id,
        package_id=package_id,
    )


def request_signup_agent_change_after_activation(
    *,
    tenant_id: str,
    package_id: str,
    requested_agent_keys: List[str],
    reason: str = "",
) -> Dict[str, Any]:
    return request_post_activation_agent_change(
        tenant_id=tenant_id,
        package_id=package_id,
        requested_agent_keys=requested_agent_keys,
        reason=reason,
    )


def signup_locked_activation_bridge_status() -> Dict[str, Any]:
    return {
        "signup_locked_activation_bridge_ready": True,
        "selection_draft_enabled": True,
        "one_time_activation_lock_enabled": True,
        "post_activation_client_changes_blocked": True,
        "owner_admin_required_for_post_activation_changes": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
