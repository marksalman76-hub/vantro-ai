from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "admin_ugc_live_media_execution_bridge.py"
main_file = ROOT / "backend" / "app" / "main.py"
doc_file = ROOT / "docs" / "admin-ugc-live-media-execution-bridge.md"

for path in [runtime_file, doc_file]:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location("admin_ugc_live_media_execution_bridge", runtime_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_admin_ugc_live_media_execution_bridge_status()

required_true = [
    "ugc_media_routing_enabled",
    "runtime_creative_execution_connected",
    "elevenlabs_adapter_connected",
    "runway_adapter_connected",
    "owner_approval_required_for_live_execution",
]

for flag in required_true:
    if status.get(flag) is not True:
        raise AssertionError(f"Expected true flag missing: {flag}")

for unsafe in ["credential_values_exposed", "external_actions_performed", "live_provider_calls_triggered"]:
    if status.get(unsafe) is not False:
        raise AssertionError(f"Unsafe status flag must be false: {unsafe}")

if module.should_route_to_ugc_live_media(
    "Create a premium UGC video ad for a lymphatic massager",
    "ugc_creative_agent",
) is not True:
    raise AssertionError("Expected UGC media task to route to live media bridge")

blocked = module.run_admin_ugc_live_media_execution(
    task="Create a premium UGC video ad for a lymphatic massager",
    owner_approved_live_execution=False,
)

if blocked.get("status") != "blocked_owner_approval_required":
    raise AssertionError("Expected owner approval block")

if blocked.get("live_provider_calls_triggered") is not False:
    raise AssertionError("Blocked execution must not trigger live provider calls")

runtime_text = runtime_file.read_text(encoding="utf-8")
doc_text = doc_file.read_text(encoding="utf-8")
main_text = main_file.read_text(encoding="utf-8", errors="ignore") if main_file.exists() else ""
combined = runtime_text + "\n" + doc_text + "\n" + main_text

required_markers = [
    "ADMIN_UGC_LIVE_MEDIA_EXECUTION_BRIDGE_READY",
    "run_admin_ugc_live_media_execution",
    "should_route_to_ugc_live_media",
    "elevenlabs",
    "runway",
    "credential_values_exposed",
]

for marker in required_markers:
    if marker not in combined:
        raise AssertionError(f"Missing marker: {marker}")

print("ADMIN_UGC_LIVE_MEDIA_EXECUTION_BRIDGE_PASSED")
