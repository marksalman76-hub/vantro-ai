from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"creative_workflow_chaining_layer_before_{STAMP}"

RUNTIME_FILE = ROOT / "backend" / "app" / "runtime" / "creative_workflow_chaining_layer.py"
DOC_FILE = ROOT / "docs" / "creative-workflow-chaining-layer.md"
TEST_FILE = ROOT / "test_creative_workflow_chaining_layer.py"

RUNTIME_CONTENT = r'''from datetime import datetime, timezone
from typing import Any, Dict, List


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


WORKFLOW_TEMPLATES = {
    "premium_voiceover_ad": [
        "script_generation",
        "elevenlabs_voiceover",
        "runway_or_kling_visual_generation",
        "export_preset_formatting",
        "quality_scoring",
    ],
    "realistic_ugc_ad": [
        "brief_analysis",
        "script_generation",
        "elevenlabs_creator_voice",
        "kling_social_video_generation",
        "brand_safe_review",
        "export_preset_formatting",
        "quality_scoring",
    ],
    "cinematic_commercial": [
        "brief_analysis",
        "script_generation",
        "elevenlabs_narration",
        "runway_cinematic_generation",
        "optional_kling_alternative_generation",
        "quality_scoring",
        "best_output_selection",
        "export_preset_formatting",
    ],
    "avatar_spokesperson_video": [
        "brief_analysis",
        "script_generation",
        "elevenlabs_voiceover",
        "heygen_avatar_generation",
        "optional_sync_lipsync_refinement",
        "brand_safe_review",
        "export_preset_formatting",
        "quality_scoring",
    ],
    "multilingual_localised_campaign": [
        "brief_analysis",
        "script_generation",
        "language_localisation",
        "elevenlabs_multilingual_voice",
        "heygen_or_kling_video_generation",
        "sync_dubbing_lipsync",
        "regional_quality_review",
        "export_preset_formatting",
        "quality_scoring",
    ],
}


def create_creative_workflow_chain(
    workflow_goal: str,
    target_platform: str = "general",
    language: str = "English",
    region: str = "",
    quality_priority: str = "high",
    owner_approved_live_execution: bool = False,
) -> Dict[str, Any]:
    goal = (workflow_goal or "").lower()

    if "avatar" in goal or "spokesperson" in goal or "presenter" in goal:
        template_key = "avatar_spokesperson_video"
    elif "multilingual" in goal or "localised" in goal or "localized" in goal or language.lower() != "english":
        template_key = "multilingual_localised_campaign"
    elif "ugc" in goal or "tiktok" in goal or "reels" in goal or "social" in goal:
        template_key = "realistic_ugc_ad"
    elif "cinematic" in goal or "commercial" in goal or "luxury" in goal:
        template_key = "cinematic_commercial"
    else:
        template_key = "premium_voiceover_ad"

    steps = WORKFLOW_TEMPLATES[template_key]

    return {
        "success": True,
        "layer": "creative_workflow_chaining_layer",
        "status": "workflow_chain_created",
        "workflow_goal": workflow_goal,
        "selected_template": template_key,
        "target_platform": target_platform,
        "language": language,
        "region": region,
        "quality_priority": quality_priority,
        "workflow_steps": steps,
        "workflow_step_count": len(steps),
        "hardcoded_single_provider_path": False,
        "multi_provider_chaining_enabled": True,
        "owner_approval_required_for_live_execution": not owner_approved_live_execution,
        "execution_allowed": bool(owner_approved_live_execution),
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "chain_rules": [
            "Create execution plans before live provider calls.",
            "Use only providers needed for the workflow goal.",
            "Live provider execution requires owner approval.",
            "Provider outputs should feed into quality scoring.",
            "Approved/rejected outputs should feed governed learning memory.",
            "Credentials must never be exposed.",
            "Tenant isolation must remain preserved.",
        ],
        "created_at": _now(),
    }


def get_creative_workflow_chaining_status() -> Dict[str, Any]:
    return {
        "success": True,
        "layer": "creative_workflow_chaining_layer",
        "status": "ready",
        "multi_provider_chaining_enabled": True,
        "workflow_template_count": len(WORKFLOW_TEMPLATES),
        "workflow_templates": WORKFLOW_TEMPLATES,
        "hardcoded_single_provider_path": False,
        "owner_approval_required_for_live_execution": True,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "supported_chains": list(WORKFLOW_TEMPLATES.keys()),
        "verified_at": _now(),
    }
'''

DOC_CONTENT = r'''# Creative Workflow Chaining Layer

## Purpose

This layer converts separate creative providers into flexible multi-step creative production workflows.

## Core Principle

Creative agents should not use every provider every time.

They should select the best workflow chain based on:
- creative goal
- platform
- language
- region
- quality priority
- owner approval
- provider suitability

## Supported Workflow Chains

1. Premium voiceover ad
2. Realistic UGC ad
3. Cinematic commercial
4. Avatar spokesperson video
5. Multilingual localised campaign

## Example Chains

### Realistic UGC Ad

Script → ElevenLabs voice → Kling video → brand-safe review → export preset → quality score

### Cinematic Commercial

Brief → script → ElevenLabs narration → Runway cinematic video → optional Kling comparison → quality score → export

### Avatar Spokesperson

Script → ElevenLabs voice → HeyGen avatar → optional Sync refinement → export → quality score

### Multilingual Campaign

Script → localisation → ElevenLabs multilingual voice → HeyGen/Kling video → Sync dubbing/lip-sync → regional review

## Governance Rules

- Live execution requires owner approval.
- Credentials must never be exposed.
- Tenant isolation must remain preserved.
- Quality scoring should guide future routing.
- Workflow chains remain flexible, not hardcoded to one provider.

## Status

CREATIVE_WORKFLOW_CHAINING_LAYER_READY
'''

TEST_CONTENT = r'''from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "creative_workflow_chaining_layer.py"
doc_file = ROOT / "docs" / "creative-workflow-chaining-layer.md"

for path in [runtime_file, doc_file]:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location("creative_workflow_chaining_layer", runtime_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_creative_workflow_chaining_status()

if status.get("multi_provider_chaining_enabled") is not True:
    raise AssertionError("Multi-provider chaining must be enabled")

if status.get("hardcoded_single_provider_path") is not False:
    raise AssertionError("Workflow must not be hardcoded to one provider")

for unsafe in ["credential_values_exposed", "external_actions_performed", "live_provider_calls_triggered"]:
    if status.get(unsafe) is not False:
        raise AssertionError(f"Unsafe flag must be false: {unsafe}")

required_templates = [
    "premium_voiceover_ad",
    "realistic_ugc_ad",
    "cinematic_commercial",
    "avatar_spokesperson_video",
    "multilingual_localised_campaign",
]

for template in required_templates:
    if template not in status.get("workflow_templates", {}):
        raise AssertionError(f"Missing workflow template: {template}")

plan = module.create_creative_workflow_chain(
    workflow_goal="Create a multilingual avatar spokesperson video",
    target_platform="Instagram Reels",
    language="Spanish",
    region="Spain",
    owner_approved_live_execution=False,
)

if plan.get("selected_template") != "avatar_spokesperson_video" and plan.get("selected_template") != "multilingual_localised_campaign":
    raise AssertionError("Expected avatar or multilingual workflow")

if plan.get("execution_allowed") is not False:
    raise AssertionError("Execution must remain blocked without owner approval")

runtime_text = runtime_file.read_text(encoding="utf-8")
doc_text = doc_file.read_text(encoding="utf-8")
combined = runtime_text + "\n" + doc_text

required_markers = [
    "CREATIVE_WORKFLOW_CHAINING_LAYER_READY",
    "create_creative_workflow_chain",
    "elevenlabs_voiceover",
    "runway_cinematic_generation",
    "kling_social_video_generation",
    "heygen_avatar_generation",
    "sync_dubbing_lipsync",
    "quality_scoring",
]

for marker in required_markers:
    if marker not in combined:
        raise AssertionError(f"Missing marker: {marker}")

print("CREATIVE_WORKFLOW_CHAINING_LAYER_PASSED")
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

    print("CREATIVE_WORKFLOW_CHAINING_LAYER_INSTALLED")
    print(f"Backup folder: {BACKUP}")
    print(f"Created/updated: {RUNTIME_FILE}")
    print(f"Created/updated: {DOC_FILE}")
    print(f"Created/updated: {TEST_FILE}")

if __name__ == "__main__":
    main()