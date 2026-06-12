from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import uuid


ROOT = Path(__file__).resolve().parents[3]
LOCAL_MEDIA_JOB_DIR = ROOT / "runtime_outputs" / "durable_media_jobs"
LOCAL_MEDIA_JOB_DIR.mkdir(parents=True, exist_ok=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_id(prefix: str = "media_job") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def safe_filename(value: str) -> str:
    return "".join(ch for ch in str(value or "") if ch.isalnum() or ch in {"_", "-"}) or safe_id()


@dataclass
class HumanMediaControls:
    human_mode: str = "No human/avatar"
    gender_presentation: str = ""
    age_range: str = ""
    ethnicity_or_cultural_appearance: str = ""
    skin_tone: str = ""
    face_shape: str = ""
    facial_features: str = ""
    hair_style: str = ""
    hair_colour: str = ""
    eye_colour: str = ""
    body_type_or_build: str = ""
    wardrobe: str = ""
    grooming: str = ""
    expressions: str = ""
    emotion: str = ""
    speaking_style: str = ""
    accent: str = ""
    body_language: str = ""
    gestures: str = ""
    eye_contact: str = ""
    posture: str = ""
    energy_level: str = ""
    realism_level: str = ""
    likeness_consistency_required: bool = True
    uploaded_likeness_asset_id: str = ""
    saved_spokesperson_id: str = ""
    explicit_likeness_consent: bool = False


@dataclass
class MediaCreativeControls:
    prompt: str = ""
    output_type: str = "Complete video with voiceover"
    platform: str = "General"
    duration_seconds: int = 30
    aspect_ratio: str = "16:9"
    language: str = "English"
    accent: str = ""
    cinematic_style: str = ""
    scene_planning: str = ""
    camera_angles: str = ""
    shot_types: str = ""
    camera_movement: str = ""
    lighting: str = ""
    color_grade: str = ""
    composition: str = ""
    transitions: str = ""
    pacing: str = ""
    realism_level: str = ""
    visual_references: List[str] = field(default_factory=list)
    props: str = ""
    environment: str = ""
    brand_style: str = ""
    product_or_service_details: str = ""
    captions: str = ""
    music_style: str = ""
    sound_effects: str = ""
    voiceover: str = ""
    voice_style: str = ""
    tone: str = ""
    emotion: str = ""
    pronunciation_notes: str = ""
    pauses: str = ""
    delivery_style: str = ""
    human: HumanMediaControls = field(default_factory=HumanMediaControls)


@dataclass
class MediaCreditEstimate:
    estimated_credits: int = 0
    duration_seconds: int = 0
    quality_mode: str = "standard"
    provider_cost_estimate: float = 0.0
    segment_count: int = 1
    includes_audio: bool = True
    includes_music: bool = False
    includes_captions: bool = False
    includes_composition: bool = True
    revision_allowance: int = 0


@dataclass
class DurableMediaJob:
    job_id: str
    status: str = "received"
    tenant_id: str = ""
    client_id: str = ""
    portal_mode: str = "admin"
    selected_agent: str = ""
    selected_agents: List[str] = field(default_factory=list)
    media_type: str = "complete_video"
    provider_plan: Dict[str, Any] = field(default_factory=dict)
    creative_controls: Dict[str, Any] = field(default_factory=dict)
    credit_estimate: Dict[str, Any] = field(default_factory=dict)
    progress: Dict[str, Any] = field(default_factory=dict)
    assets: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    error: str = ""
    customer_safe: bool = True
    credential_values_exposed: bool = False
    internal_config_exposed: bool = False
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)


class LocalDurableMediaJobStore:
    """
    Local JSON implementation of the production MediaJobStore contract.

    This is intentionally designed so the implementation can later be swapped to:
    - RDS PostgreSQL for durable job state
    - SQS for queue messages
    - S3 for asset payloads

    Do not store provider credentials in jobs.
    """

    def __init__(self, root: Optional[Path] = None):
        self.root = Path(root or LOCAL_MEDIA_JOB_DIR)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, job_id: str) -> Path:
        return self.root / f"{safe_filename(job_id)}.json"

    def create_job(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        job_id = str(payload.get("job_id") or safe_id("durable_media_job"))

        creative_controls = payload.get("creative_controls")
        if not isinstance(creative_controls, dict):
            creative_controls = self.normalise_creative_controls(payload)

        credit_estimate = payload.get("credit_estimate")
        if not isinstance(credit_estimate, dict):
            credit_estimate = self.estimate_credits(creative_controls)

        job = DurableMediaJob(
            job_id=job_id,
            status=str(payload.get("status") or "received"),
            tenant_id=str(payload.get("tenant_id") or payload.get("client_id") or ""),
            client_id=str(payload.get("client_id") or ""),
            portal_mode=str(payload.get("portal_mode") or payload.get("mode") or "admin"),
            selected_agent=str(payload.get("selected_agent") or payload.get("agent_id") or ""),
            selected_agents=list(payload.get("selected_agents") or payload.get("agent_ids") or []),
            media_type=str(payload.get("media_type") or "complete_video"),
            provider_plan=dict(payload.get("provider_plan") or {}),
            creative_controls=creative_controls,
            credit_estimate=credit_estimate,
            progress=dict(payload.get("progress") or {"stage": "received", "percent": 0}),
            events=[],
            customer_safe=True,
            credential_values_exposed=False,
            internal_config_exposed=False,
        )

        job.events.append({
            "event": "job_created",
            "status": job.status,
            "created_at": utc_now(),
            "customer_safe": True,
        })

        return self.save_job(asdict(job))

    def save_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        clean = dict(job or {})
        clean["job_id"] = str(clean.get("job_id") or safe_id("durable_media_job"))
        clean["updated_at"] = utc_now()
        clean["customer_safe"] = True
        clean["credential_values_exposed"] = False
        clean["internal_config_exposed"] = False

        path = self._path(clean["job_id"])
        temp = path.with_suffix(".json.tmp")
        temp.write_text(json.dumps(clean, indent=2, default=str), encoding="utf-8")
        temp.replace(path)
        return clean

    def get_job(self, job_id: str) -> Dict[str, Any]:
        path = self._path(job_id)
        if not path.exists():
            return {
                "success": False,
                "job_id": job_id,
                "status": "not_found",
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return {
                **data,
                "success": True,
                "customer_safe": True,
                "credential_values_exposed": False,
                "internal_config_exposed": False,
            }
        except Exception as error:
            return {
                "success": False,
                "job_id": job_id,
                "status": "read_failed",
                "error": str(error)[:500],
                "customer_safe": True,
                "credential_values_exposed": False,
            }

    def update_status(
        self,
        job_id: str,
        status: str,
        progress: Optional[Dict[str, Any]] = None,
        event: Optional[Dict[str, Any]] = None,
        **fields: Any,
    ) -> Dict[str, Any]:
        job = self.get_job(job_id)
        if not job.get("success"):
            job = {
                "job_id": job_id,
                "status": "received",
                "events": [],
                "assets": [],
                "created_at": utc_now(),
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        job["status"] = status
        if progress is not None:
            job["progress"] = progress

        for key, value in fields.items():
            job[key] = value

        events = list(job.get("events") or [])
        events.append({
            "event": (event or {}).get("event") or "status_updated",
            "status": status,
            "at": utc_now(),
            **dict(event or {}),
            "customer_safe": True,
        })
        job["events"] = events

        return self.save_job(job)

    def add_asset(self, job_id: str, asset: Dict[str, Any]) -> Dict[str, Any]:
        job = self.get_job(job_id)
        if not job.get("success"):
            return job

        assets = list(job.get("assets") or [])
        assets.append({
            **dict(asset or {}),
            "added_at": utc_now(),
            "customer_safe": True,
            "credential_values_exposed": False,
        })
        job["assets"] = assets
        return self.save_job(job)

    def list_jobs(self, limit: int = 50) -> Dict[str, Any]:
        files = sorted(self.root.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        jobs = []
        for path in files[: max(1, int(limit))]:
            try:
                jobs.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue

        return {
            "success": True,
            "count": len(jobs),
            "jobs": jobs,
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    def normalise_creative_controls(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        human_payload = payload.get("human") if isinstance(payload.get("human"), dict) else {}

        human = HumanMediaControls(
            human_mode=str(payload.get("human_mode") or human_payload.get("human_mode") or "No human/avatar"),
            gender_presentation=str(payload.get("gender_presentation") or human_payload.get("gender_presentation") or ""),
            age_range=str(payload.get("age_range") or human_payload.get("age_range") or ""),
            ethnicity_or_cultural_appearance=str(payload.get("ethnicity_or_cultural_appearance") or payload.get("ethnicity") or human_payload.get("ethnicity_or_cultural_appearance") or ""),
            skin_tone=str(payload.get("skin_tone") or human_payload.get("skin_tone") or ""),
            face_shape=str(payload.get("face_shape") or human_payload.get("face_shape") or ""),
            facial_features=str(payload.get("facial_features") or human_payload.get("facial_features") or ""),
            hair_style=str(payload.get("hair_style") or human_payload.get("hair_style") or ""),
            hair_colour=str(payload.get("hair_colour") or payload.get("hair_color") or human_payload.get("hair_colour") or ""),
            eye_colour=str(payload.get("eye_colour") or payload.get("eye_color") or human_payload.get("eye_colour") or ""),
            body_type_or_build=str(payload.get("body_type_or_build") or payload.get("body_type") or human_payload.get("body_type_or_build") or ""),
            wardrobe=str(payload.get("wardrobe") or human_payload.get("wardrobe") or ""),
            grooming=str(payload.get("grooming") or human_payload.get("grooming") or ""),
            expressions=str(payload.get("expressions") or payload.get("facial_expressions") or human_payload.get("expressions") or ""),
            emotion=str(payload.get("emotion") or human_payload.get("emotion") or ""),
            speaking_style=str(payload.get("speaking_style") or human_payload.get("speaking_style") or ""),
            accent=str(payload.get("accent") or human_payload.get("accent") or ""),
            body_language=str(payload.get("body_language") or human_payload.get("body_language") or ""),
            gestures=str(payload.get("gestures") or human_payload.get("gestures") or ""),
            eye_contact=str(payload.get("eye_contact") or human_payload.get("eye_contact") or ""),
            posture=str(payload.get("posture") or human_payload.get("posture") or ""),
            energy_level=str(payload.get("energy_level") or human_payload.get("energy_level") or ""),
            realism_level=str(payload.get("realism_level") or human_payload.get("realism_level") or ""),
            likeness_consistency_required=True,
            uploaded_likeness_asset_id=str(payload.get("uploaded_likeness_asset_id") or human_payload.get("uploaded_likeness_asset_id") or ""),
            saved_spokesperson_id=str(payload.get("saved_spokesperson_id") or human_payload.get("saved_spokesperson_id") or ""),
            explicit_likeness_consent=bool(payload.get("explicit_likeness_consent") or human_payload.get("explicit_likeness_consent") or False),
        )

        controls = MediaCreativeControls(
            prompt=str(payload.get("prompt") or payload.get("task") or payload.get("creative_brief") or ""),
            output_type=str(payload.get("output_type") or "Complete video with voiceover"),
            platform=str(payload.get("platform") or "General"),
            duration_seconds=int(float(payload.get("duration_seconds") or payload.get("duration") or 30)),
            aspect_ratio=str(payload.get("aspect_ratio") or "16:9"),
            language=str(payload.get("language") or "English"),
            accent=str(payload.get("accent") or ""),
            cinematic_style=str(payload.get("cinematic_style") or ""),
            scene_planning=str(payload.get("scene_planning") or ""),
            camera_angles=str(payload.get("camera_angles") or ""),
            shot_types=str(payload.get("shot_types") or ""),
            camera_movement=str(payload.get("camera_movement") or ""),
            lighting=str(payload.get("lighting") or payload.get("lighting_style") or ""),
            color_grade=str(payload.get("color_grade") or ""),
            composition=str(payload.get("composition") or ""),
            transitions=str(payload.get("transitions") or ""),
            pacing=str(payload.get("pacing") or ""),
            realism_level=str(payload.get("realism_level") or ""),
            visual_references=list(payload.get("visual_references") or []),
            props=str(payload.get("props") or ""),
            environment=str(payload.get("environment") or payload.get("background_setting") or ""),
            brand_style=str(payload.get("brand_style") or ""),
            product_or_service_details=str(payload.get("product_or_service_details") or ""),
            captions=str(payload.get("captions") or payload.get("subtitles") or ""),
            music_style=str(payload.get("music_style") or ""),
            sound_effects=str(payload.get("sound_effects") or payload.get("sfx") or ""),
            voiceover=str(payload.get("voiceover") or payload.get("voiceover_script") or ""),
            voice_style=str(payload.get("voice_style") or ""),
            tone=str(payload.get("tone") or ""),
            emotion=str(payload.get("emotion") or ""),
            pronunciation_notes=str(payload.get("pronunciation_notes") or ""),
            pauses=str(payload.get("pauses") or ""),
            delivery_style=str(payload.get("delivery_style") or ""),
            human=human,
        )

        return asdict(controls)

    def estimate_credits(self, controls: Dict[str, Any]) -> Dict[str, Any]:
        duration = int(float(controls.get("duration_seconds") or 30))
        segment_count = max(1, (duration + 9) // 10)
        includes_audio = "voice" in str(controls.get("output_type") or "").lower() or bool(controls.get("voiceover"))
        includes_captions = bool(controls.get("captions"))
        includes_music = bool(controls.get("music_style"))
        estimated = segment_count * 10
        if includes_audio:
            estimated += max(2, duration // 10)
        if includes_music:
            estimated += max(2, duration // 15)
        if includes_captions:
            estimated += max(1, duration // 20)
        estimated += segment_count * 2  # composition/stitching allowance

        return asdict(MediaCreditEstimate(
            estimated_credits=estimated,
            duration_seconds=duration,
            quality_mode=str(controls.get("quality_mode") or "standard"),
            provider_cost_estimate=0.0,
            segment_count=segment_count,
            includes_audio=includes_audio,
            includes_music=includes_music,
            includes_captions=includes_captions,
            includes_composition=True,
            revision_allowance=0,
        ))


def get_media_job_store() -> LocalDurableMediaJobStore:
    return LocalDurableMediaJobStore()
