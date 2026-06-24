"""
Composio integration service.

Provides Anthropic-format tool definitions and executes actions
via Composio REST API on behalf of a workspace.

Security contract:
- api_key is NEVER logged or returned to callers.
- Financial transfer tools are hard-blocked (no HITL override).
- get_available_tools() silently returns [] on any failure; it must
  never raise so that agent execution is not blocked.
- All credential access goes through encryption_service.decrypt(),
  which is the only entry point for reading stored secrets.
"""
import logging

import httpx
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

COMPOSIO_BASE = "https://backend.composio.dev/api/v1"

# Only whitelisted apps are exposed as agent tools.
# Financial / payment apps are intentionally absent.
SAFE_APP_WHITELIST = {
    "gmail", "slack", "github", "notion", "hubspot", "shopify",
    "airtable", "googlesheets", "googledocs", "calendly", "stripe",
    "mailchimp", "intercom", "zendesk", "pipedrive", "asana", "trello",
    "jira", "discord", "twitter", "linkedin",
}

# Tool name substrings that must never be executed autonomously.
_FINANCIAL_KEYWORDS = {
    "transfer", "payment", "charge", "withdraw", "send_money", "wire",
}


# ---------------------------------------------------------------------------
# Credential helpers
# ---------------------------------------------------------------------------

def get_composio_credentials(db: Session, workspace_id: str) -> tuple[str, str] | None:
    """
    Return (api_key, entity_id) for the workspace, or None if not configured.

    Reads two WorkspaceIntegration rows:
      - integration_key = "COMPOSIO_API_KEY"   → the Composio API key
      - integration_key = "COMPOSIO_ENTITY_ID" → the entity identifier (default: "default")

    Raw values are decrypted here only; never returned beyond this function's
    callers, never logged.
    """
    from app.models.agent_system import WorkspaceIntegration
    from app.services.encryption_service import decrypt

    try:
        key_row = (
            db.query(WorkspaceIntegration)
            .filter(
                WorkspaceIntegration.workspace_id == workspace_id,
                WorkspaceIntegration.integration_key == "COMPOSIO_API_KEY",
                WorkspaceIntegration.is_active == True,
            )
            .first()
        )
        if not key_row:
            return None

        api_key = decrypt(key_row.encrypted_value)

        entity_row = (
            db.query(WorkspaceIntegration)
            .filter(
                WorkspaceIntegration.workspace_id == workspace_id,
                WorkspaceIntegration.integration_key == "COMPOSIO_ENTITY_ID",
                WorkspaceIntegration.is_active == True,
            )
            .first()
        )
        entity_id = decrypt(entity_row.encrypted_value) if entity_row else "default"

        return api_key, entity_id
    except Exception:
        logger.exception("Failed to retrieve Composio credentials for workspace %s", workspace_id)
        return None


# ---------------------------------------------------------------------------
# Tool discovery
# ---------------------------------------------------------------------------

def get_available_tools(api_key: str, entity_id: str = "default") -> list[dict]:
    """
    Fetch connected apps for the entity and return Anthropic-format tool definitions.

    Only exposes whitelisted, safe apps. Never exposes financial transfer tools.
    Always returns a list (empty on any error) — must not raise.
    """
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(
                f"{COMPOSIO_BASE}/connectedAccounts",
                headers={"x-api-key": api_key},
                params={"entityId": entity_id, "status": "ACTIVE"},
            )
            resp.raise_for_status()
            connected = resp.json().get("items", [])

        app_names = [
            item["appUniqueId"]
            for item in connected
            if item.get("appUniqueId", "").lower() in SAFE_APP_WHITELIST
        ]
        if not app_names:
            return []

        tools: list[dict] = []
        with httpx.Client(timeout=15) as client:
            for app in app_names[:5]:  # cap at 5 apps to limit tool count
                try:
                    resp = client.get(
                        f"{COMPOSIO_BASE}/actions",
                        headers={"x-api-key": api_key},
                        params={"apps": app, "limit": 10, "filterImportantActions": True},
                    )
                    if resp.status_code != 200:
                        continue
                    for action in resp.json().get("items", []):
                        tool = _action_to_anthropic_tool(action)
                        if tool:
                            tools.append(tool)
                except Exception:
                    # Skip this app on any per-app error; continue with others
                    logger.debug("Composio: failed to fetch actions for app %s", app)
                    continue

        return tools
    except Exception:
        # Non-blocking: agent execution must continue even if Composio is unavailable
        logger.debug("Composio: get_available_tools failed silently")
        return []


# ---------------------------------------------------------------------------
# Tool execution
# ---------------------------------------------------------------------------

def execute_tool(
    api_key: str,
    entity_id: str,
    tool_name: str,
    tool_input: dict,
) -> str:
    """
    Execute a Composio action and return a string result for the tool_result block.

    Financial transfer tools are hard-blocked regardless of caller intent.
    """
    # Hard security block — financial transfer tools cannot be called autonomously
    if any(keyword in tool_name.lower() for keyword in _FINANCIAL_KEYWORDS):
        return (
            "[BLOCKED] Financial transfer tools require explicit owner approval "
            "and cannot be executed autonomously by an agent."
        )

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f"{COMPOSIO_BASE}/actions/{tool_name}/execute",
                headers={
                    "x-api-key": api_key,
                    "Content-Type": "application/json",
                },
                json={"entityId": entity_id, "input": tool_input},
            )
            resp.raise_for_status()
            data = resp.json()

        if data.get("successfull") or data.get("success"):
            result = data.get("data") or data.get("response", {})
            return f"[COMPOSIO OK] {str(result)[:2000]}"
        else:
            return f"[COMPOSIO ERROR] {data.get('error', 'Unknown error')}"

    except httpx.HTTPStatusError as e:
        return (
            f"[COMPOSIO HTTP ERROR] {e.response.status_code}: "
            f"{e.response.text[:500]}"
        )
    except Exception as e:
        return f"[COMPOSIO ERROR] {str(e)[:500]}"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _action_to_anthropic_tool(action: dict) -> dict | None:
    """Convert a Composio action schema dict to an Anthropic tool definition."""
    name = action.get("name", "")
    if not name:
        return None

    # Anthropic tool names must match ^[a-zA-Z0-9_-]+$
    safe_name = name.replace(".", "_").replace(" ", "_")
    # Strip any remaining invalid characters
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in ("_", "-"))
    safe_name = safe_name[:64]
    if not safe_name:
        return None

    params = action.get("parameters", {}) or {}
    description = (
        action.get("description")
        or action.get("displayName")
        or name
    )

    return {
        "name": safe_name,
        "description": str(description)[:500],
        "input_schema": {
            "type": "object",
            "properties": params.get("properties", {}),
            "required": params.get("required", []),
        },
    }
