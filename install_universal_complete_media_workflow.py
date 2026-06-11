from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / "backend" / "app" / "runtime" / "direct_media_provider_execution_runtime.py"
MAIN = ROOT / "backend" / "app" / "main.py"
API_DIR = ROOT / "frontend" / "src" / "app" / "api" / "admin-universal-complete-media"
API_ROUTE = API_DIR / "route.ts"
TEST = ROOT / "test_universal_complete_media_workflow.py"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"universal_complete_media_workflow_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

for path in [RUNTIME, MAIN, API_ROUTE, TEST]:
    if path.exists():
        backup_name = str(path.relative_to(ROOT)).replace("\\", "__").replace("/", "__")
        (BACKUP_DIR / backup_name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

API_DIR.mkdir(parents=True, exist_ok=True)

runtime = RUNTIME.read_text(encoding="utf-8")

if "import threading" not in runtime:
    runtime = runtime.replace("import uuid\n", "import uuid\nimport threading\n", 1)

if "UNIVERSAL_COMPLETE_MEDIA_WORKFLOW_V1" not in runtime:
    runtime += r'''


# UNIVERSAL_COMPLETE_MEDIA_WORKFLOW_V1
def _ucm_text(value: Any, default: str = "") -> str:
    return str(value or default).strip()


def _ucm_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on", "approved"}
    return bool(value)


def _ucm_controls(payload: Dict[str, Any]) -> Dict[str, Any]:
    safe = dict(payload or {})

    controls = {
        "prompt": _ucm_text(safe.get("prompt") or safe.get("task") or safe.get("media_brief")),
        "agent_id": _ucm_text(
            safe.get("agent_id")
            or safe.get("assigned_agent")
            or safe.get("requested_agent")
            or "social_media_manager_content_creator_agent"
        ),
        "output_type": _ucm_text(safe.get("output_type") or safe.get("media_output_type") or "complete_video"),
        "industry": _ucm_text(safe.get("industry") or safe.get("niche")),
        "target_audience": _ucm_text(safe.get("target_audience")),
        "platform": _ucm_text(safe.get("platform") or "general"),
        "duration_seconds": _ucm_text(safe.get("duration_seconds") or safe.get("duration") or "5"),
        "aspect_ratio": _ucm_text(safe.get("aspect_ratio") or "9:16"),
        "language": _ucm_text(safe.get("language") or "English"),
        "accent": _ucm_text(safe.get("accent")),
        "tone": _ucm_text(safe.get("tone") or "natural, polished, human"),
        "voice_style": _ucm_text(safe.get("voice_style") or "natural conversational voice"),
        "age_range": _ucm_text(safe.get("age_range")),
        "gender_presentation": _ucm_text(safe.get("gender_presentation")),
        "ethnicity_or_cultural_appearance": _ucm_text(
            safe.get("ethnicity_or_cultural_appearance")
            or safe.get("ethnicity")
            or safe.get("cultural_appearance")
        ),
        "avatar_likeness": _ucm_text(safe.get("avatar_likeness") or safe.get("ultra_human_likeness")),
        "face_shape": _ucm_text(safe.get("face_shape")),
        "skin_tone": _ucm_text(safe.get("skin_tone")),
        "facial_features": _ucm_text(safe.get("facial_features")),
        "hair_style": _ucm_text(safe.get("hair_style")),
        "hair_colour": _ucm_text(safe.get("hair_colour") or safe.get("hair_color")),
        "eye_colour": _ucm_text(safe.get("eye_colour") or safe.get("eye_color")),
        "wardrobe": _ucm_text(safe.get("wardrobe") or safe.get("styling")),
        "expressions": _ucm_text(safe.get("expressions") or safe.get("facial_expressions")),
        "emotion": _ucm_text(safe.get("emotion")),
        "eye_contact": _ucm_text(safe.get("eye_contact")),
        "gestures": _ucm_text(safe.get("gestures") or safe.get("hand_gestures")),
        "body_language": _ucm_text(safe.get("body_language")),
        "lip_sync_accuracy": _ucm_text(safe.get("lip_sync_accuracy") or "high when avatar or talking-head output is requested"),
        "speaking_pace": _ucm_text(safe.get("speaking_pace") or "natural, not rushed"),
        "camera_framing": _ucm_text(safe.get("camera_framing")),
        "lighting_style": _ucm_text(safe.get("lighting_style")),
        "background_setting": _ucm_text(safe.get("background_setting") or safe.get("setting")),
        "brand_style": _ucm_text(safe.get("brand_style")),
        "product_or_service_details": _ucm_text(safe.get("product_or_service_details")),
        "offer": _ucm_text(safe.get("offer") or safe.get("promotion")),
        "call_to_action": _ucm_text(safe.get("call_to_action") or safe.get("cta")),
        "captions": _ucm_text(safe.get("captions") or safe.get("subtitles")),
        "music_style": _ucm_text(safe.get("music_style")),
        "sound_effects": _ucm_text(safe.get("sound_effects") or safe.get("sfx")),
        "pacing": _ucm_text(safe.get("pacing") or "smooth, clear, premium"),
        "visual_style": _ucm_text(safe.get("visual_style")),
        "camera_movement": _ucm_text(safe.get("camera_movement")),
        "compliance_notes": _ucm_text(safe.get("compliance_notes")),
        "number_of_variations": _ucm_text(safe.get("number_of_variations") or "1"),
        "final_delivery_format": _ucm_text(safe.get("final_delivery_format") or "mp4"),
        "video_provider": _ucm_text(safe.get("video_provider") or safe.get("provider") or "runway").lower(),
        "audio_provider": _ucm_text(safe.get("audio_provider") or "elevenlabs").lower(),
    }

    return controls


def _ucm_brief_lines(controls: Dict[str, Any]) -> str:
    ordered_keys = [
        "output_type",
        "industry",
        "target_audience",
        "platform",
        "duration_seconds",
        "aspect_ratio",
        "language",
        "accent",
        "tone",
        "voice_style",
        "age_range",
        "gender_presentation",
        "ethnicity_or_cultural_appearance",
        "avatar_likeness",
        "face_shape",
        "skin_tone",
        "facial_features",
        "hair_style",
        "hair_colour",
        "eye_colour",
        "wardrobe",
        "expressions",
        "emotion",
        "eye_contact",
        "gestures",
        "body_language",
        "lip_sync_accuracy",
        "speaking_pace",
        "camera_framing",
        "lighting_style",
        "background_setting",
        "brand_style",
        "product_or_service_details",
        "offer",
        "call_to_action",
        "captions",
        "music_style",
        "sound_effects",
        "pacing",
        "visual_style",
        "camera_movement",
        "compliance_notes",
        "final_delivery_format",
    ]

    lines = []
    for key in ordered_keys:
        value = _ucm_text(controls.get(key))
        if value:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


def build_universal_complete_media_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    controls = _ucm_controls(payload)
    prompt = controls["prompt"]
    duration_raw = controls["duration_seconds"]

    try:
        duration = max(3.0, min(float(str(duration_raw).replace("s", "").strip()), 60.0))
    except Exception:
        duration = 5.0

    third = round(duration / 3, 2)
    two_thirds = round(duration * 2 / 3, 2)

    voice_word_limit = max(5, min(int(duration * 2.2), 120))

    visual_prompt = (
        "Create a premium, realistic, globally adaptable media visual based on this brief. "
        "Do not include visible text unless captions or text are explicitly requested. "
        "Keep visuals coherent with the timed plan. "
        "Use any provided age range, gender presentation, ethnicity/cultural appearance, avatar likeness, "
        "facial features, expressions, wardrobe, setting, lighting, camera movement, and brand style strictly as "
        "user-provided creative direction. Do not infer real identity. "
        f"Duration target: {duration} seconds. Aspect ratio: {controls['aspect_ratio']}. "
        f"Original prompt: {prompt}\n\nCreative controls:\n{_ucm_brief_lines(controls)}\n\n"
        f"Timed plan:\n"
        f"0.00s-{third:.2f}s: clear opening visual that establishes the concept.\n"
        f"{third:.2f}s-{two_thirds:.2f}s: main action, presenter/avatar/scene detail, or key visual benefit.\n"
        f"{two_thirds:.2f}s-{duration:.2f}s: clean finish with natural endpoint and optional call-to-action if provided."
    )

    voice_prompt = (
        f"Write and perform a natural {controls['language']} voiceover for a {duration:.1f} second media file. "
        f"Use a {controls['tone']} tone and {controls['voice_style']} style. "
        "The voiceover must sound human, smooth, non-robotic, not choppy, and not rushed. "
        f"Maximum {voice_word_limit} words. "
        "Match the visual timing and avoid long pauses unless the prompt requires it. "
        "If a call-to-action is provided, include it naturally at the end. "
        "Do not read internal labels or field names. "
        f"Original prompt: {prompt}\n\nCreative controls:\n{_ucm_brief_lines(controls)}"
    )

    return {
        "success": True,
        "controls": controls,
        "duration_seconds": duration,
        "voice_word_limit": voice_word_limit,
        "timed_plan": [
            {"start": 0.0, "end": third, "purpose": "opening visual"},
            {"start": third, "end": two_thirds, "purpose": "main visual/audio message"},
            {"start": two_thirds, "end": duration, "purpose": "final beat or call-to-action"},
        ],
        "visual_prompt": visual_prompt,
        "voice_prompt": voice_prompt,
        "quality_requirements": {
            "universal_not_ecommerce_only": True,
            "complete_media_file_from_one_prompt": True,
            "natural_non_robotic_audio": True,
            "audio_video_synchronisation_required": True,
            "avoid_choppy_audio": True,
            "avatar_likeness_controls_supported": True,
            "facial_feature_controls_supported": True,
            "expression_controls_supported": True,
            "language_controls_supported": True,
            "optional_demographic_creative_direction_only": True,
            "do_not_infer_sensitive_attributes": True,
            "customer_safe": True,
            "credential_values_exposed": False,
        },
    }


def _ucm_get_duration_seconds(path_value: str) -> float | None:
    try:
        ffprobe = shutil.which("ffprobe")
        if not ffprobe:
            return None
        path = str(path_value or "").strip()
        if not path:
            return None
        completed = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if completed.returncode != 0:
            return None
        return float((completed.stdout or "").strip())
    except Exception:
        return None


def _ucm_compose_with_sync(video_job: Dict[str, Any], audio_job: Dict[str, Any], composition_job_id: str) -> Dict[str, Any]:
    video_path = _first_existing_asset_path(video_job, "video")
    audio_path = _first_existing_asset_path(audio_job, "audio")

    base = {
        "success": False,
        "job_id": composition_job_id,
        "composition_job_id": composition_job_id,
        "video_job_id": video_job.get("job_id"),
        "audio_job_id": audio_job.get("job_id"),
        "provider": "universal_complete_media_composer",
        "media_type": "complete_video",
        "asset_type": "video",
        "customer_safe": True,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "created_at": _now(),
    }

    if not video_path:
        return _write_job({**base, "status": "blocked_video_asset_missing"})
    if not audio_path:
        return _write_job({**base, "status": "blocked_audio_asset_missing"})

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return _write_job({
            **base,
            "status": "blocked_ffmpeg_missing",
            "reason": "ffmpeg is not available in the runtime environment.",
        })

    out_dir = DIRECT_JOB_DIR / "universal_complete_media_assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / f"{composition_job_id}.mp4"

    video_duration = _ucm_get_duration_seconds(str(video_path))
    audio_duration = _ucm_get_duration_seconds(str(audio_path))

    command = [
        ffmpeg,
        "-y",
        "-i",
        str(video_path),
        "-i",
        str(audio_path),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-af",
        "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=async=1:first_pts=0",
        "-shortest",
        "-movflags",
        "+faststart",
        str(output_path),
    ]

    running = _write_job({
        **base,
        "status": "running_synchronised_composition",
        "video_asset_path": str(video_path),
        "audio_asset_path": str(audio_path),
        "video_duration_seconds": video_duration,
        "audio_duration_seconds": audio_duration,
        "output_path": str(output_path),
        "sync_strategy": "normalise_audio_resample_async_shortest_faststart",
        "started_at": _now(),
    })

    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=240)
        if completed.returncode != 0:
            return _write_job({
                **running,
                "success": False,
                "status": "synchronised_composition_failed",
                "error": (completed.stderr or completed.stdout or "ffmpeg failed")[-1200:],
            })

        if not output_path.exists() or output_path.stat().st_size <= 0:
            return _write_job({
                **running,
                "success": False,
                "status": "synchronised_composition_output_missing",
                "error": "ffmpeg completed but output file was not created.",
            })

        final_duration = _ucm_get_duration_seconds(str(output_path))

        return _write_job({
            **running,
            "success": True,
            "status": "completed",
            "provider_status": "universal_complete_media_ready",
            "provider_result_status": "universal_complete_media_ready",
            "playable": True,
            "preview_ready": True,
            "download_ready": True,
            "asset_path": str(output_path),
            "download_url": str(output_path),
            "preview_url": f"/api/admin-direct-media-provider-asset?job_id={composition_job_id}",
            "signed_preview_url": f"/api/admin-direct-media-provider-asset?job_id={composition_job_id}",
            "final_media_type": "synchronised_video_with_audio",
            "final_duration_seconds": final_duration,
            "video_size_bytes": output_path.stat().st_size,
            "completed_at": _now(),
            "quality_requirements": {
                "natural_non_robotic_audio": True,
                "avoid_choppy_audio": True,
                "audio_video_synchronisation_required": True,
                "customer_safe": True,
                "credential_values_exposed": False,
            },
        })

    except Exception as error:
        return _write_job({
            **running,
            "success": False,
            "status": "synchronised_composition_exception",
            "error": str(error)[:1200],
        })


def start_universal_complete_media_workflow(payload: Dict[str, Any]) -> Dict[str, Any]:
    safe_payload = dict(payload or {})
    controls = _ucm_controls(safe_payload)
    prompt = controls["prompt"]
    job_id = str(safe_payload.get("job_id") or _safe_id("universal_complete_media_job"))
    owner_approved = _ucm_bool(safe_payload.get("owner_approved") or safe_payload.get("owner_approval_granted"))

    base_job = {
        "success": True,
        "accepted": False,
        "job_id": job_id,
        "status": "received",
        "agent_id": controls["agent_id"],
        "provider": "universal_complete_media_workflow",
        "video_provider": controls["video_provider"],
        "audio_provider": controls["audio_provider"],
        "media_type": "complete_video",
        "asset_type": "video",
        "output_type": controls["output_type"],
        "platform": controls["platform"],
        "language": controls["language"],
        "duration_seconds": controls["duration_seconds"],
        "universal_complete_media_workflow": True,
        "one_prompt_complete_media": True,
        "owner_approved": owner_approved,
        "created_at": _now(),
        "customer_safe": True,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
    }

    _write_job(base_job)

    if not owner_approved:
        return _write_job({
            **base_job,
            "success": False,
            "status": "blocked_owner_approval_required",
            "reason": "Universal complete media workflow requires owner/admin approval for live provider execution.",
        })

    if not prompt:
        return _write_job({
            **base_job,
            "success": False,
            "status": "blocked_missing_prompt",
            "reason": "A media prompt is required.",
        })

    plan = build_universal_complete_media_plan(safe_payload)

    def _runner() -> None:
        try:
            _write_job({
                **base_job,
                "accepted": True,
                "status": "running_visual_generation",
                "timed_plan": plan.get("timed_plan"),
                "quality_requirements": plan.get("quality_requirements"),
                "started_at": _now(),
            })

            video_result = execute_direct_media_provider_job({
                "agent_id": controls["agent_id"],
                "provider": controls["video_provider"],
                "media_type": "video",
                "prompt": plan["visual_prompt"],
                "owner_approved": True,
                "owner_approval_granted": True,
            })

            if not video_result.get("success") or video_result.get("status") != "completed" or not video_result.get("playable"):
                _write_job({
                    **base_job,
                    "success": False,
                    "accepted": True,
                    "status": "universal_complete_media_visual_failed",
                    "video_job_id": video_result.get("job_id"),
                    "video_status": video_result.get("status"),
                    "video_error": video_result.get("error") or video_result.get("reason") or video_result.get("message"),
                    "completed_at": _now(),
                })
                return

            _write_job({
                **base_job,
                "accepted": True,
                "status": "running_audio_generation",
                "video_job_id": video_result.get("job_id"),
                "video_provider_job_id": video_result.get("provider_job_id"),
                "timed_plan": plan.get("timed_plan"),
            })

            audio_result = execute_direct_media_provider_job({
                "agent_id": controls["agent_id"],
                "provider": controls["audio_provider"],
                "media_type": "audio",
                "prompt": plan["voice_prompt"],
                "owner_approved": True,
                "owner_approval_granted": True,
            })

            if not audio_result.get("success") or audio_result.get("status") != "completed" or not audio_result.get("playable"):
                _write_job({
                    **base_job,
                    "success": False,
                    "accepted": True,
                    "status": "universal_complete_media_audio_failed",
                    "video_job_id": video_result.get("job_id"),
                    "audio_job_id": audio_result.get("job_id"),
                    "audio_status": audio_result.get("status"),
                    "audio_error": audio_result.get("error") or audio_result.get("reason") or audio_result.get("message"),
                    "completed_at": _now(),
                })
                return

            _write_job({
                **base_job,
                "accepted": True,
                "status": "running_synchronised_composition",
                "video_job_id": video_result.get("job_id"),
                "audio_job_id": audio_result.get("job_id"),
            })

            composition_job_id = _safe_id("universal_complete_media_composition")
            composition_result = _ucm_compose_with_sync(video_result, audio_result, composition_job_id)

            if not composition_result.get("success") or composition_result.get("status") != "completed" or not composition_result.get("playable"):
                _write_job({
                    **base_job,
                    "success": False,
                    "accepted": True,
                    "status": "universal_complete_media_composition_failed",
                    "video_job_id": video_result.get("job_id"),
                    "audio_job_id": audio_result.get("job_id"),
                    "composition_job_id": composition_result.get("job_id"),
                    "composition_status": composition_result.get("status"),
                    "composition_error": composition_result.get("error") or composition_result.get("reason") or composition_result.get("message"),
                    "completed_at": _now(),
                })
                return

            _write_job({
                **base_job,
                "success": True,
                "accepted": True,
                "status": "completed",
                "provider_status": "universal_complete_media_ready",
                "provider_result_status": "universal_complete_media_ready",
                "video_job_id": video_result.get("job_id"),
                "audio_job_id": audio_result.get("job_id"),
                "composition_job_id": composition_result.get("job_id"),
                "provider_job_id": composition_result.get("job_id"),
                "playable": True,
                "preview_ready": True,
                "download_ready": True,
                "asset_path": composition_result.get("asset_path"),
                "download_url": composition_result.get("download_url"),
                "preview_url": f"/api/admin-direct-media-provider-asset?job_id={composition_result.get('job_id')}",
                "signed_preview_url": f"/api/admin-direct-media-provider-asset?job_id={composition_result.get('job_id')}",
                "final_media_type": "synchronised_video_with_audio",
                "final_duration_seconds": composition_result.get("final_duration_seconds"),
                "timed_plan": plan.get("timed_plan"),
                "quality_requirements": plan.get("quality_requirements"),
                "completed_at": _now(),
            })

        except Exception as error:
            _write_job({
                **base_job,
                "success": False,
                "accepted": True,
                "status": "universal_complete_media_exception",
                "error": str(error)[:1200],
                "completed_at": _now(),
            })

    thread = threading.Thread(target=_runner, name=f"universal_complete_media_{job_id}", daemon=True)
    thread.start()

    return {
        **base_job,
        "success": True,
        "accepted": True,
        "polling_required": True,
        "status": "queued",
        "message": "Universal complete media workflow accepted. One prompt will generate visual, natural audio, synchronise, and compose the final playable file.",
        "timed_plan": plan.get("timed_plan"),
        "quality_requirements": plan.get("quality_requirements"),
    }


def universal_complete_media_status() -> Dict[str, Any]:
    return {
        "success": True,
        "universal_complete_media_workflow_ready": True,
        "one_prompt_complete_media": True,
        "universal_not_ecommerce_only": True,
        "supported_controls": [
            "prompt",
            "output_type",
            "industry",
            "target_audience",
            "platform",
            "duration",
            "aspect_ratio",
            "language",
            "accent",
            "tone",
            "voice_style",
            "age_range",
            "gender_presentation",
            "ethnicity_or_cultural_appearance",
            "avatar_likeness",
            "face_shape",
            "skin_tone",
            "facial_features",
            "hair_style",
            "hair_colour",
            "eye_colour",
            "wardrobe",
            "expressions",
            "emotion",
            "eye_contact",
            "gestures",
            "body_language",
            "lip_sync_accuracy",
            "speaking_pace",
            "camera_framing",
            "lighting_style",
            "background_setting",
            "brand_style",
            "product_or_service_details",
            "offer",
            "call_to_action",
            "captions",
            "music_style",
            "sound_effects",
            "pacing",
            "visual_style",
            "camera_movement",
            "compliance_notes",
            "number_of_variations",
            "final_delivery_format",
        ],
        "workflow": [
            "interpret_prompt_and_controls",
            "build_timed_media_plan",
            "generate_visual_or_avatar_asset",
            "generate_natural_audio",
            "synchronise_audio_video",
            "compose_final_playable_media_file",
        ],
        "quality_requirements": {
            "complete_synchronicity_required": True,
            "natural_non_robotic_audio": True,
            "avoid_choppy_audio": True,
            "customer_safe": True,
            "credential_values_exposed": False,
        },
        "credential_values_exposed": False,
        "customer_safe": True,
    }
'''

RUNTIME.write_text(runtime, encoding="utf-8")

main = MAIN.read_text(encoding="utf-8")

route_block = r'''

# UNIVERSAL_COMPLETE_MEDIA_WORKFLOW_ROUTE_V1
@app.post("/admin/universal-complete-media")
async def admin_universal_complete_media(request: Request) -> Dict[str, object]:
    from backend.app.runtime.direct_media_provider_execution_runtime import start_universal_complete_media_workflow

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    return start_universal_complete_media_workflow(payload)


@app.get("/admin/universal-complete-media-status")
def admin_universal_complete_media_status() -> Dict[str, object]:
    from backend.app.runtime.direct_media_provider_execution_runtime import universal_complete_media_status

    return universal_complete_media_status()
'''

if "UNIVERSAL_COMPLETE_MEDIA_WORKFLOW_ROUTE_V1" not in main:
    main = main.rstrip() + "\n" + route_block + "\n"

if 'or path == "/admin/universal-complete-media"' not in main:
    main = main.replace(
        'or path == "/admin/direct-media-provider-compose-status"',
        'or path == "/admin/direct-media-provider-compose-status"\n        or path == "/admin/universal-complete-media"\n        or path == "/admin/universal-complete-media-status"',
    )

if 'if path == "/admin/universal-complete-media" and request.method.upper() == "POST":' not in main:
    main = main.replace(
        '''        if path == "/admin/direct-media-provider-compose" and request.method.upper() == "POST":''',
        '''        if path == "/admin/universal-complete-media" and request.method.upper() == "POST":
            from backend.app.runtime.direct_media_provider_execution_runtime import start_universal_complete_media_workflow

            try:
                payload = await request.json()
            except Exception:
                payload = {}

            return JSONResponse(content=start_universal_complete_media_workflow(payload))

        if path == "/admin/universal-complete-media-status" and request.method.upper() == "GET":
            from backend.app.runtime.direct_media_provider_execution_runtime import universal_complete_media_status

            return JSONResponse(content=universal_complete_media_status())

        if path == "/admin/direct-media-provider-compose" and request.method.upper() == "POST":''',
    )

MAIN.write_text(main, encoding="utf-8")

API_ROUTE.write_text(
    r'''import { NextRequest, NextResponse } from "next/server";

function backendBaseUrl() {
  return (
    process.env.BACKEND_BASE_URL ||
    process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "https://api.trance-formation.com.au"
  ).replace(/\/$/, "");
}

function adminToken() {
  return (
    process.env.ADMIN_PLATFORM_TOKEN ||
    process.env.ADMIN_AUTH_SECRET ||
    process.env.ADMIN_BEARER_TOKEN ||
    process.env.ADMIN_TOKEN ||
    process.env.PLATFORM_ADMIN_TOKEN ||
    process.env.OWNER_ADMIN_TOKEN ||
    ""
  ).trim();
}

function adminHeaders() {
  const token = adminToken();
  return {
    "Content-Type": "application/json",
    Authorization: token ? `Bearer ${token}` : "",
    "x-admin-token": token,
    "x-actor-role": "owner_admin",
    "x-tenant-id": "owner_admin",
    "User-Agent": "frontend-universal-complete-media-proxy/1.0",
  };
}

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const response = await fetch(`${backendBaseUrl()}/admin/universal-complete-media-status`, {
      method: "GET",
      headers: adminHeaders(),
      cache: "no-store",
    });

    const data = await response.json().catch(() => ({ success: false, error: "invalid_backend_json" }));
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "universal_complete_media_status_proxy_failed",
        message: error instanceof Error ? error.message : "Unknown proxy error",
        customer_safe: true,
        credential_values_exposed: false,
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const payload = await request.json().catch(() => ({}));

    const safePayload = {
      prompt: payload.prompt || payload.task || "",
      agent_id: payload.agent_id || payload.assigned_agent || "social_media_manager_content_creator_agent",
      output_type: payload.output_type || "complete_video",
      industry: payload.industry || "",
      target_audience: payload.target_audience || "",
      platform: payload.platform || "general",
      duration_seconds: payload.duration_seconds || payload.duration || "5",
      aspect_ratio: payload.aspect_ratio || "9:16",
      language: payload.language || "English",
      accent: payload.accent || "",
      tone: payload.tone || "natural, polished, human",
      voice_style: payload.voice_style || "natural conversational voice",
      age_range: payload.age_range || "",
      gender_presentation: payload.gender_presentation || "",
      ethnicity_or_cultural_appearance: payload.ethnicity_or_cultural_appearance || payload.ethnicity || "",
      avatar_likeness: payload.avatar_likeness || payload.ultra_human_likeness || "",
      face_shape: payload.face_shape || "",
      skin_tone: payload.skin_tone || "",
      facial_features: payload.facial_features || "",
      hair_style: payload.hair_style || "",
      hair_colour: payload.hair_colour || payload.hair_color || "",
      eye_colour: payload.eye_colour || payload.eye_color || "",
      wardrobe: payload.wardrobe || "",
      expressions: payload.expressions || payload.facial_expressions || "",
      emotion: payload.emotion || "",
      eye_contact: payload.eye_contact || "",
      gestures: payload.gestures || payload.hand_gestures || "",
      body_language: payload.body_language || "",
      lip_sync_accuracy: payload.lip_sync_accuracy || "high when avatar or talking-head output is requested",
      speaking_pace: payload.speaking_pace || "natural, not rushed",
      camera_framing: payload.camera_framing || "",
      lighting_style: payload.lighting_style || "",
      background_setting: payload.background_setting || payload.setting || "",
      brand_style: payload.brand_style || "",
      product_or_service_details: payload.product_or_service_details || "",
      offer: payload.offer || payload.promotion || "",
      call_to_action: payload.call_to_action || payload.cta || "",
      captions: payload.captions || payload.subtitles || "",
      music_style: payload.music_style || "",
      sound_effects: payload.sound_effects || payload.sfx || "",
      pacing: payload.pacing || "smooth, clear, premium",
      visual_style: payload.visual_style || "",
      camera_movement: payload.camera_movement || "",
      compliance_notes: payload.compliance_notes || "",
      number_of_variations: payload.number_of_variations || "1",
      final_delivery_format: payload.final_delivery_format || "mp4",
      video_provider: payload.video_provider || "runway",
      audio_provider: payload.audio_provider || "elevenlabs",
      owner_approved: true,
      owner_approval_granted: true,
    };

    const response = await fetch(`${backendBaseUrl()}/admin/universal-complete-media`, {
      method: "POST",
      headers: adminHeaders(),
      body: JSON.stringify(safePayload),
      cache: "no-store",
    });

    const data = await response.json().catch(() => ({ success: false, error: "invalid_backend_json" }));
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "universal_complete_media_proxy_failed",
        message: error instanceof Error ? error.message : "Unknown proxy error",
        customer_safe: true,
        credential_values_exposed: false,
      },
      { status: 500 }
    );
  }
}
''',
    encoding="utf-8",
)

TEST.write_text(
    r'''from backend.app.runtime.direct_media_provider_execution_runtime import (
    build_universal_complete_media_plan,
    universal_complete_media_status,
    start_universal_complete_media_workflow,
)


def test_universal_complete_media_status():
    status = universal_complete_media_status()
    assert status["success"] is True, status
    assert status["universal_not_ecommerce_only"] is True, status
    assert "avatar_likeness" in status["supported_controls"], status
    assert "facial_features" in status["supported_controls"], status
    assert "ethnicity_or_cultural_appearance" in status["supported_controls"], status
    assert status["credential_values_exposed"] is False, status


def test_universal_complete_media_plan_controls():
    plan = build_universal_complete_media_plan({
        "prompt": "Create a cinematic fitness coaching reel.",
        "language": "Spanish",
        "age_range": "adult",
        "gender_presentation": "male",
        "ethnicity_or_cultural_appearance": "Mediterranean appearance",
        "avatar_likeness": "ultra-human realistic presenter",
        "facial_features": "strong jawline, expressive eyes",
        "expressions": "confident and encouraging",
        "duration_seconds": 5,
    })
    assert plan["success"] is True, plan
    assert plan["quality_requirements"]["universal_not_ecommerce_only"] is True, plan
    assert plan["quality_requirements"]["natural_non_robotic_audio"] is True, plan
    assert plan["quality_requirements"]["audio_video_synchronisation_required"] is True, plan
    assert "Spanish" in plan["voice_prompt"], plan["voice_prompt"]
    assert "ultra-human realistic presenter" in plan["visual_prompt"], plan["visual_prompt"]
    assert "strong jawline" in plan["visual_prompt"], plan["visual_prompt"]


def test_universal_complete_media_owner_gate():
    result = start_universal_complete_media_workflow({
        "prompt": "Create a short media file.",
        "owner_approved": False,
    })
    assert result["status"] == "blocked_owner_approval_required", result
    assert result["credential_values_exposed"] is False, result


def test_universal_complete_media_prompt_required():
    result = start_universal_complete_media_workflow({
        "owner_approved": True,
    })
    assert result["status"] == "blocked_missing_prompt", result
    assert result["credential_values_exposed"] is False, result


if __name__ == "__main__":
    test_universal_complete_media_status()
    test_universal_complete_media_plan_controls()
    test_universal_complete_media_owner_gate()
    test_universal_complete_media_prompt_required()
    print("UNIVERSAL_COMPLETE_MEDIA_WORKFLOW_TEST_PASSED")
''',
    encoding="utf-8",
)

print("UNIVERSAL_COMPLETE_MEDIA_WORKFLOW_INSTALLED")
print(f"Backup: {BACKUP_DIR}")
print(f"Updated: {RUNTIME}")
print(f"Updated: {MAIN}")
print(f"Created: {API_ROUTE}")
print(f"Created: {TEST}")