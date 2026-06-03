from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "admin_creative_media_asset_viewer.py"
main_file = ROOT / "backend" / "app" / "main.py"
doc_file = ROOT / "docs" / "admin-creative-media-asset-viewer.md"

for path in [runtime_file, main_file, doc_file]:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location("admin_creative_media_asset_viewer", runtime_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_admin_creative_media_asset_viewer_status()
assets = module.get_admin_creative_media_assets(limit=20)

if status.get("media_asset_viewer_enabled") is not True:
    raise AssertionError("Media asset viewer must be enabled")

for unsafe in ["credential_values_exposed", "external_actions_performed", "live_provider_calls_triggered"]:
    if status.get(unsafe) is not False:
        raise AssertionError(f"Unsafe flag must be false: {unsafe}")
    if assets.get(unsafe) is not False:
        raise AssertionError(f"Unsafe asset flag must be false: {unsafe}")

if "runway" not in status.get("providers_checked", []):
    raise AssertionError("Runway provider folder must be checked")

if "elevenlabs" not in status.get("providers_checked", []):
    raise AssertionError("ElevenLabs provider folder must be checked")

runtime_text = runtime_file.read_text(encoding="utf-8")
main_text = main_file.read_text(encoding="utf-8", errors="ignore")
doc_text = doc_file.read_text(encoding="utf-8")

combined = runtime_text + "\n" + main_text + "\n" + doc_text

required_markers = [
    "ADMIN_CREATIVE_MEDIA_ASSET_VIEWER_READY",
    "get_admin_creative_media_assets",
    "get_admin_creative_media_asset_viewer_status",
    "/admin/creative/media-assets",
    "/admin/creative/media-assets/status",
    "credential_values_exposed",
]

for marker in required_markers:
    if marker not in combined:
        raise AssertionError(f"Missing marker: {marker}")

print("ADMIN_CREATIVE_MEDIA_ASSET_VIEWER_PASSED")
