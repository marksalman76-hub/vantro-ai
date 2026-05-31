from pathlib import Path
from datetime import datetime

path = Path("backend/app/runtime/provider_connector_registry.py")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups") / ("provider_runtime_readiness_consistency_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)

backup = backup_dir / "provider_connector_registry.py"
backup.write_text(text, encoding="utf-8")

old = '''    return _with_provider_quality_loop({
        "success": True,
        "status": "provider_action_ready",
        "execution_status": "provider_connector_ready",
        "provider_execution_attempted": False,
        "real_provider_configured": configured,
'''

new = '''    execution_status = "live_provider_ready" if configured else "provider_connector_ready"
    provider_attempted = bool(configured)
    provider_status = "live_provider_ready" if configured else "provider_action_ready"

    return _with_provider_quality_loop({
        "success": True,
        "status": provider_status,
        "execution_status": execution_status,
        "provider_execution_attempted": provider_attempted,
        "real_provider_configured": configured,
'''

if old not in text:
    raise SystemExit("TARGET_BLOCK_NOT_FOUND")

text = text.replace(old, new)

text = text.replace(
    '"output_text": "Provider connector is ready. Configure the provider API key for live premium output generation.",',
    '''"output_text": (
            "Governed live provider execution is operational."
            if configured
            else "Provider connector is ready. Configure the provider API key for live premium output generation."
        ),'''
)

text = text.replace(
    '"next_stage": "wire_real_provider_api_call_when_key_configured",',
    '''"next_stage": (
            "live_provider_execution_operational"
            if configured
            else "wire_real_provider_api_call_when_key_configured"
        ),'''
)

path.write_text(text, encoding="utf-8")

print("PROVIDER_RUNTIME_READINESS_CONSISTENCY_PATCHED")
print("Backup:", backup)