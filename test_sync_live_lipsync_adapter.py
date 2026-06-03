from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "sync_live_lipsync_adapter.py"
doc_file = ROOT / "docs" / "sync-live-lipsync-adapter.md"

for path in [runtime_file, doc_file]:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location("sync_live_lipsync_adapter", runtime_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_sync_live_lipsync_adapter_status()

if status.get("credential_values_exposed") is not False:
    raise AssertionError("Credential values must not be exposed")

if status.get("live_execution_requires_explicit_allow") is not True:
    raise AssertionError("Live execution must require explicit allow flag")

blocked = module.run_sync_lipsync_quality_test(
    video_url="https://example.com/video.mp4",
    audio_url="https://example.com/audio.wav",
    allow_live_execution=False,
)

if blocked.get("status") != "blocked_owner_approval_required":
    raise AssertionError("Adapter must block live execution unless explicitly allowed")

if blocked.get("live_provider_call_triggered") is not False:
    raise AssertionError("Blocked test must not trigger provider calls")

runtime_text = runtime_file.read_text(encoding="utf-8")
doc_text = doc_file.read_text(encoding="utf-8")
combined = runtime_text + "\n" + doc_text

required_markers = [
    "SYNC_LIVE_LIPSYNC_ADAPTER_READY",
    "run_sync_lipsync_quality_test",
    "allow_live_execution",
    "x-api-key",
    "sync-3",
    "/v2/generate",
    "credential_values_exposed",
    "runtime_outputs",
]

for marker in required_markers:
    if marker not in combined:
        raise AssertionError(f"Missing marker: {marker}")

print("SYNC_LIVE_LIPSYNC_ADAPTER_PASSED")
