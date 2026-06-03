from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "creative_provider_credential_activation_checks.py"
main_file = ROOT / "backend" / "app" / "main.py"
doc_file = ROOT / "docs" / "creative-provider-credential-activation-checks.md"

required_files = [runtime_file, main_file, doc_file]

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location(
    "creative_provider_credential_activation_checks",
    runtime_file,
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_creative_provider_credential_activation_checks()
client_status = module.get_client_safe_creative_provider_credential_activation_checks()

required_providers = [
    "runway",
    "kling",
    "heygen",
    "elevenlabs",
    "lipsync_dubbing",
    "music_sfx",
    "upscaling",
]

provider_keys = [provider["provider_key"] for provider in status["providers"]]

for provider in required_providers:
    if provider not in provider_keys:
        raise AssertionError(f"Missing provider activation check: {provider}")

required_true_flags = [
    "owner_activation_required_for_paid_providers",
    "tenant_isolation_preserved",
    "customer_safe_visibility_preserved",
]

for flag in required_true_flags:
    if status.get(flag) is not True:
        raise AssertionError(f"Expected true flag missing or false: {flag}")

required_false_flags = [
    "credential_values_exposed",
    "external_actions_performed",
    "live_provider_calls_triggered",
    "live_execution_globally_enabled",
]

for flag in required_false_flags:
    if status.get(flag) is not False:
        raise AssertionError(f"Unsafe flag must be false: {flag}")

    if client_status.get(flag) is not False:
        raise AssertionError(f"Client unsafe flag must be false: {flag}")

runtime_text = runtime_file.read_text(encoding="utf-8")
main_text = main_file.read_text(encoding="utf-8")
doc_text = doc_file.read_text(encoding="utf-8")

combined_text = runtime_text + "\n" + main_text + "\n" + doc_text

required_markers = [
    "CREATIVE_PROVIDER_CREDENTIAL_ACTIVATION_CHECKS_READY",
    "/creative/provider-credential-activation-checks",
    "/admin/creative/provider-credential-activation-checks",
    "RUNWAY_API_KEY",
    "KLING_API_KEY",
    "HEYGEN_API_KEY",
    "ELEVENLABS_API_KEY",
]

for marker in required_markers:
    if marker not in combined_text:
        raise AssertionError(f"Missing marker: {marker}")

print("CREATIVE_PROVIDER_CREDENTIAL_ACTIVATION_CHECKS_PASSED")
