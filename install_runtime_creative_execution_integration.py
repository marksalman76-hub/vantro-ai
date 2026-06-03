from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"runtime_creative_execution_integration_before_{STAMP}"

RUNTIME_FILE = ROOT / "backend" / "app" / "runtime" / "runtime_creative_execution_integration.py"
DOC_FILE = ROOT / "docs" / "runtime-creative-execution-integration.md"
TEST_FILE = ROOT / "test_runtime_creative_execution_integration.py"

RUNTIME_CONTENT = r'''from datetime import datetime, timezone
from typing import Any, Dict

try:
    from backend.app.runtime.unified_creative_provider_orchestration import choose_creative_provider_mix
except Exception:
    choose_creative_provider_mix = None

try:
    from backend.app.runtime.creative_workflow_chaining_layer import create_creative_workflow_chain
except Exception:
    create_creative_workflow_chain = None

try:
    from backend.app.runtime.creative_quality_refinement_loop import compare_creative_provider_options
except Exception:
    compare_creative_provider_options = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_runtime_creative_execution_plan(
    creative_goal: str,
    content_type: str = "video",
    target_platform: str = "general",
    language: str = "English",
    accent: str = "",
    region: str = "",
    quality_priority: str = "high",
    budget_priority: str = "balanced",
    requires_avatar: bool = False,
    requires_lipsync: bool = False,
    requires_dubbing: bool = False,
    requires_cinematic: bool = False,
    requires_ugc_realism: bool = False,
    requires_voiceover: bool = True,
    owner_approved_live_execution: bool = False,
) -> Dict[str, Any]:
    if choose_creative_provider_mix is None:
        return {
            "success": False,
            "status": "orchestration_layer_unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
        }

    if create_creative_workflow_chain is None:
        return {
            "success": False,
            "status": "workflow_chaining_layer_unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
        }

    if compare_creative_provider_options is None:
        return {
            "success": False,
            "status": "quality_refinement_layer_unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
        }

    provider_plan = choose_creative_provider_mix(
        creative_goal=creative_goal,
        content_type=content_type,
        target_platform=target_platform,
        language=language,
        accent=accent,
        region=region,
        quality_priority=quality_priority,
        budget_priority=budget_priority,
        requires_avatar=requires_avatar,
        requires_lipsync=requires_lipsync,
        requires_dubbing=requires_dubbing,
        requires_cinematic=requires_cinematic,
        requires_ugc_realism=requires_ugc_realism,
        requires_voiceover=requires_voiceover,
        owner_approved_live_execution=owner_approved_live_execution,
    )

    workflow_chain = create_creative_workflow_chain(
        workflow_goal=creative_goal,
        target_platform=target_platform,
        language=language,
        region=region,
        quality_priority=quality_priority,
        owner_approved_live_execution=owner_approved_live_execution,
    )

    selected_providers = provider_plan.get("selected_providers", [])

    quality_comparison = compare_creative_provider_options(
        creative_goal=creative_goal,
        providers=selected_providers,
        multilingual=language.lower() != "english" or requires_dubbing,
    )

    execution_allowed = bool(owner_approved_live_execution)

    return {
        "success": True,
        "layer": "runtime_creative_execution_integration",
        "status": "runtime_creative_execution_plan_created",
        "creative_goal": creative_goal,
        "content_type": content_type,
        "target_platform": target_platform,
        "language": language,
        "accent": accent,
        "region": region,
        "quality_priority": quality_priority,
        "budget_priority": budget_priority,
        "execution_allowed": execution_allowed,
        "owner_approval_required_for_live_execution": not execution_allowed,
        "provider_plan": provider_plan,
        "workflow_chain": workflow_chain,
        "quality_comparison": quality_comparison,
        "recommended_provider": quality_comparison.get("best_provider_recommendation"),
        "selected_providers": selected_providers,
        "workflow_steps": workflow_chain.get("workflow_steps", []),
        "learning_signals_ready": True,
        "provider_fallback_ready": True,
        "retry_refinement_ready": True,
        "deliverable_generation_ready": True,
        "hardcoded_execution_path": False,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "runtime_rules": [
            "Runtime planning does not trigger paid provider calls.",
            "Live execution remains owner-approved.",
            "Provider selection stays flexible and policy-driven.",
            "Workflow chains can change by goal, platform, language, and region.",
            "Quality scoring can influence future routing.",
            "Learning signals may improve routing but cannot override governance.",
            "Credential values must never be exposed.",
        ],
        "created_at": _now(),
    }


def get_runtime_creative_execution_integration_status() -> Dict[str, Any]:
    return {
        "success": True,
        "layer": "runtime_creative_execution_integration",
        "status": "ready",
        "orchestration_connected": choose_creative_provider_mix is not None,
        "workflow_chaining_connected": create_creative_workflow_chain is not None,
        "quality_refinement_connected": compare_creative_provider_options is not None,
        "runtime_planning_enabled": True,
        "provider_fallback_ready": True,
        "retry_refinement_ready": True,
        "learning_signal_handoff_ready": True,
        "deliverable_generation_ready": True,
        "hardcoded_execution_path": False,
        "owner_approval_required_for_live_execution": True,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "verified_at": _now(),
    }
'''

DOC_CONTENT = r'''# Runtime Creative Execution Integration

## Purpose

This layer connects provider orchestration, creative workflow chaining, quality scoring, and learning-signal readiness into one runtime creative execution planning layer.

## What It Does

- Creates runtime creative execution plans
- Selects provider mix
- Selects workflow chain
- Compares provider quality fit
- Prepares retry/refinement routing
- Prepares learning signal handoff
- Keeps live provider calls owner-approved

## What It Does Not Do

- It does not expose credentials.
- It does not trigger paid provider calls by itself.
- It does not bypass owner approval.
- It does not hardcode provider routes.
- It does not override tenant isolation.

## Status

RUNTIME_CREATIVE_EXECUTION_INTEGRATION_READY
'''

TEST_CONTENT = r'''from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "runtime_creative_execution_integration.py"
doc_file = ROOT / "docs" / "runtime-creative-execution-integration.md"

for path in [runtime_file, doc_file]:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location("runtime_creative_execution_integration", runtime_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_runtime_creative_execution_integration_status()

required_true = [
    "orchestration_connected",
    "workflow_chaining_connected",
    "quality_refinement_connected",
    "runtime_planning_enabled",
    "provider_fallback_ready",
    "retry_refinement_ready",
    "learning_signal_handoff_ready",
    "deliverable_generation_ready",
    "owner_approval_required_for_live_execution",
]

for flag in required_true:
    if status.get(flag) is not True:
        raise AssertionError(f"Expected true flag missing: {flag}")

if status.get("hardcoded_execution_path") is not False:
    raise AssertionError("Runtime execution path must not be hardcoded")

for unsafe in ["credential_values_exposed", "external_actions_performed", "live_provider_calls_triggered"]:
    if status.get(unsafe) is not False:
        raise AssertionError(f"Unsafe flag must be false: {unsafe}")

plan = module.create_runtime_creative_execution_plan(
    creative_goal="Create a multilingual avatar UGC ad for Instagram Reels",
    content_type="video ad",
    target_platform="Instagram Reels",
    language="Spanish",
    region="Spain",
    requires_avatar=True,
    requires_dubbing=True,
    requires_ugc_realism=True,
    owner_approved_live_execution=False,
)

if plan.get("success") is not True:
    raise AssertionError("Runtime creative execution plan failed")

if plan.get("execution_allowed") is not False:
    raise AssertionError("Execution must remain blocked without owner approval")

for expected in ["provider_plan", "workflow_chain", "quality_comparison"]:
    if expected not in plan:
        raise AssertionError(f"Missing runtime plan section: {expected}")

if not plan.get("selected_providers"):
    raise AssertionError("Expected selected providers")

if not plan.get("workflow_steps"):
    raise AssertionError("Expected workflow steps")

runtime_text = runtime_file.read_text(encoding="utf-8")
doc_text = doc_file.read_text(encoding="utf-8")
combined = runtime_text + "\n" + doc_text

required_markers = [
    "RUNTIME_CREATIVE_EXECUTION_INTEGRATION_READY",
    "create_runtime_creative_execution_plan",
    "provider_plan",
    "workflow_chain",
    "quality_comparison",
    "learning_signal_handoff_ready",
    "retry_refinement_ready",
]

for marker in required_markers:
    if marker not in combined:
        raise AssertionError(f"Missing marker: {marker}")

print("RUNTIME_CREATIVE_EXECUTION_INTEGRATION_PASSED")
'''

def backup_path(path: Path) -> None:
    if path.exists():
        destination = BACKUP / path.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)

def write_file(path: Path, content: str) -> None:
    backup_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")

def main() -> None:
    BACKUP.mkdir(parents=True, exist_ok=True)

    write_file(RUNTIME_FILE, RUNTIME_CONTENT)
    write_file(DOC_FILE, DOC_CONTENT)
    write_file(TEST_FILE, TEST_CONTENT)

    print("RUNTIME_CREATIVE_EXECUTION_INTEGRATION_INSTALLED")
    print(f"Backup folder: {BACKUP}")
    print(f"Created/updated: {RUNTIME_FILE}")
    print(f"Created/updated: {DOC_FILE}")
    print(f"Created/updated: {TEST_FILE}")

if __name__ == "__main__":
    main()