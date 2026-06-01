from pathlib import Path

p = Path("backend/app/runtime/real_action_execution_bridge.py")
text = p.read_text(encoding="utf-8")

old = '''    deliverable = {
        "deliverable_id": f"deliverable_{uuid4().hex[:12]}",
        "type": action_type,
        "title": f"Executed: {str(implementation_action)[:90]}",
        "summary": adapter_execution.get("output") or str(implementation_action),
        "created_by_agent": assigned_agent,
        "customer_safe": True,
        "asset_status": adapter_execution.get("asset", {}).get("status", "created"),
        "download_ready": adapter_execution.get("asset", {}).get("download_ready", False),
        "preview_ready": adapter_execution.get("asset", {}).get("preview_ready", True),
        "actions_performed": adapter_execution.get("actions_performed", []),
        "adapter": adapter_execution.get("adapter"),
        "asset": adapter_execution.get("asset"),
        "content": {
            "headline": f"{assigned_agent} executed an operational adapter.",
            "body": adapter_execution.get("output") or str(implementation_action),
            "next_step": "Review the created operational actions, then approve client delivery or request amendment.",
        },
    }'''

new = '''    adapter_asset = adapter_execution.get("asset") or {}
    preview_url = adapter_execution.get("preview_url") or adapter_execution.get("asset_url") or adapter_execution.get("media_url") or adapter_asset.get("preview_url") or adapter_asset.get("asset_url") or ""
    asset_url = adapter_execution.get("asset_url") or adapter_execution.get("media_url") or adapter_asset.get("asset_url") or preview_url
    media_url = adapter_execution.get("media_url") or asset_url
    generated_files = adapter_execution.get("generated_files") or adapter_asset.get("generated_files") or []

    deliverable = {
        "deliverable_id": f"deliverable_{uuid4().hex[:12]}",
        "type": action_type,
        "title": f"Executed: {str(implementation_action)[:90]}",
        "summary": adapter_execution.get("output") or str(implementation_action),
        "created_by_agent": assigned_agent,
        "customer_safe": True,
        "asset_status": adapter_asset.get("status", "created"),
        "download_ready": adapter_asset.get("download_ready", False),
        "preview_ready": adapter_asset.get("preview_ready", True),
        "preview_url": preview_url,
        "asset_url": asset_url,
        "media_url": media_url,
        "generated_files": generated_files,
        "actions_performed": adapter_execution.get("actions_performed", []),
        "adapter": adapter_execution.get("adapter"),
        "asset": {
            **adapter_asset,
            "preview_url": preview_url,
            "asset_url": asset_url,
            "media_url": media_url,
            "generated_files": generated_files,
        },
        "content": {
            "headline": f"{assigned_agent} executed an operational adapter.",
            "body": adapter_execution.get("output") or str(implementation_action),
            "next_step": "Review the created operational actions, then approve client delivery or request amendment.",
        },
    }'''

if old not in text:
    raise SystemExit("deliverable block not found")

text = text.replace(old, new, 1)

old_return = '''        "customer_safe_message": adapter_execution.get("output"),
        "actions_performed": adapter_execution.get("actions_performed", []),
        "deliverable": deliverable,
        "created_at": _now(),'''

new_return = '''        "customer_safe_message": adapter_execution.get("output"),
        "preview_url": preview_url,
        "asset_url": asset_url,
        "media_url": media_url,
        "generated_files": generated_files,
        "actions_performed": adapter_execution.get("actions_performed", []),
        "deliverable": deliverable,
        "created_at": _now(),'''

text = text.replace(old_return, new_return, 1)

p.write_text(text, encoding="utf-8")
print("REAL_ACTION_BRIDGE_ASSET_PASSTHROUGH_FIXED")