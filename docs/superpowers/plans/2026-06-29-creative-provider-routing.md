# Creative Provider Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build one canonical creative provider routing layer so every creative-capable Vantro agent can resolve Higgsfield video models and Nano Banana image models consistently.

**Architecture:** Add a pure backend routing module that owns creative agent normalization, media-type detection, quality normalization, and provider/model selection. Then make provider status metadata and admin/worker execution paths consume that routing module instead of hand-maintaining scattered creative provider lists.

**Tech Stack:** Python 3, FastAPI backend, SQLAlchemy job records, pytest backend tests, Next.js admin UI request context.

## Global Constraints

- Video `720p` routes to Higgsfield model `Kling 3.0 Turbo`.
- Video `1080p` routes to Higgsfield model `Kling 3.0`.
- Video `4K` routes to Higgsfield model `Cinema Studio 4K`.
- Image standard or production requests route to `Nano Banana 2`.
- Image premium or pro requests route to `Nano Banana Pro`.
- Unknown or missing video quality defaults to `1080p` and therefore `Kling 3.0`.
- Unknown or missing image tier defaults to standard and therefore `Nano Banana 2`.
- Credential values must never be logged, returned, or stored in generated artifacts.
- Existing governance, approval, credit, and package checks remain in place.
- The deployed backend must not depend on local Claude Code MCP authentication.

---

## File Structure

- Create `backend/app/runtime/creative_provider_routing.py`
  - Single source of truth for creative agent IDs, aliases, provider capabilities, quality normalization, and route resolution.
- Create `backend/tests/test_creative_provider_routing.py`
  - Unit tests for all creative agents, aliases, video quality mapping, image tier mapping, and defaults.
- Modify `backend/app/runtime/audio_visual_provider_stack.py`
  - Reuse canonical creative agent IDs and expose Higgsfield/Nano Banana provider status metadata.
- Modify `backend/app/routes/admin.py`
  - Enrich admin agent run context with `creative_provider_route` when the selected agent is creative-capable.
- Modify `backend/app/agents/agent_worker.py`
  - Use `is_creative_agent()` instead of only checking `ugc_media_agent`, and pass the canonical route to the provider adapter payload.
- Modify `backend/app/integrations/execution_adapters.py`
  - Include selected provider/model metadata in the adapter result and call Higgsfield with the selected video model when executing video.

---

### Task 1: Canonical Creative Provider Routing Contract

**Files:**
- Create: `backend/app/runtime/creative_provider_routing.py`
- Test: `backend/tests/test_creative_provider_routing.py`

**Interfaces:**
- Produces: `CREATIVE_AGENT_IDS: set[str]`
- Produces: `CREATIVE_AGENT_ALIASES: dict[str, str]`
- Produces: `normalize_creative_agent_id(agent_id: str) -> str`
- Produces: `is_creative_agent(agent_id: str) -> bool`
- Produces: `resolve_creative_provider_route(agent_id: str, media_type: str = "both", video_quality: str = "", image_tier: str = "", request_context: dict | None = None) -> dict`
- Produces: `creative_provider_status() -> dict`

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_creative_provider_routing.py`:

```python
import pytest

from app.runtime.creative_provider_routing import (
    CREATIVE_AGENT_IDS,
    creative_provider_status,
    is_creative_agent,
    normalize_creative_agent_id,
    resolve_creative_provider_route,
)


CREATIVE_AGENT_CASES = [
    "ugc_media_agent",
    "ugc_creative_agent",
    "product_image_agent",
    "ad_creative_agent",
    "creative_rotation_agent",
    "social_media_content_agent",
    "ads_optimisation_agent",
]


@pytest.mark.parametrize("agent_id", CREATIVE_AGENT_CASES)
def test_every_creative_agent_resolves_video_models(agent_id):
    route = resolve_creative_provider_route(
        agent_id=agent_id,
        media_type="video",
        video_quality="720p",
    )

    assert route["success"] is True
    assert route["agent_id"] == agent_id
    assert route["canonical_agent_id"] in CREATIVE_AGENT_IDS
    assert route["video"]["provider"] == "higgsfield"
    assert route["video"]["model"] == "Kling 3.0 Turbo"
    assert route["video"]["quality"] == "720p"
    assert route["credential_values_exposed"] is False


@pytest.mark.parametrize("agent_id", CREATIVE_AGENT_CASES)
def test_every_creative_agent_resolves_image_models(agent_id):
    route = resolve_creative_provider_route(
        agent_id=agent_id,
        media_type="image",
        image_tier="premium",
    )

    assert route["success"] is True
    assert route["image"]["provider"] == "nano_banana"
    assert route["image"]["model"] == "Nano Banana Pro"
    assert route["image"]["tier"] == "premium"
    assert route["credential_values_exposed"] is False


@pytest.mark.parametrize(
    ("quality", "expected_model"),
    [
        ("720p", "Kling 3.0 Turbo"),
        ("1080p", "Kling 3.0"),
        ("4K", "Cinema Studio 4K"),
        ("", "Kling 3.0"),
        ("unknown", "Kling 3.0"),
    ],
)
def test_video_quality_selects_higgsfield_model(quality, expected_model):
    route = resolve_creative_provider_route(
        agent_id="ugc_media_agent",
        media_type="video",
        video_quality=quality,
    )

    assert route["video"]["provider"] == "higgsfield"
    assert route["video"]["model"] == expected_model


@pytest.mark.parametrize(
    ("tier", "expected_model"),
    [
        ("standard", "Nano Banana 2"),
        ("production", "Nano Banana 2"),
        ("", "Nano Banana 2"),
        ("premium", "Nano Banana Pro"),
        ("pro", "Nano Banana Pro"),
    ],
)
def test_image_tier_selects_nano_banana_model(tier, expected_model):
    route = resolve_creative_provider_route(
        agent_id="product_image_agent",
        media_type="image",
        image_tier=tier,
    )

    assert route["image"]["provider"] == "nano_banana"
    assert route["image"]["model"] == expected_model


@pytest.mark.parametrize(
    ("alias", "canonical"),
    [
        ("paid_ads_agent", "ads_optimisation_agent"),
        ("social_media_manager_content_creator_agent", "social_media_content_agent"),
        ("product_video_agent", "ugc_media_agent"),
    ],
)
def test_alias_ids_resolve_to_canonical_creative_agents(alias, canonical):
    assert normalize_creative_agent_id(alias) == canonical
    assert is_creative_agent(alias) is True


def test_unknown_agent_returns_clear_failure():
    route = resolve_creative_provider_route(
        agent_id="finance_admin_agent",
        media_type="video",
    )

    assert route["success"] is False
    assert route["reason"] == "unknown_creative_agent"
    assert route["credential_values_exposed"] is False


def test_creative_provider_status_exposes_models_without_credentials():
    status = creative_provider_status()

    assert status["success"] is True
    assert status["providers"]["higgsfield"]["models"] == [
        "Kling 3.0 Turbo",
        "Kling 3.0",
        "Cinema Studio 4K",
    ]
    assert status["providers"]["nano_banana"]["models"] == [
        "Nano Banana 2",
        "Nano Banana Pro",
    ]
    assert status["credential_values_exposed"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run from repo root:

```bash
cd backend
pytest tests/test_creative_provider_routing.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.runtime.creative_provider_routing'`.

- [ ] **Step 3: Implement the routing module**

Create `backend/app/runtime/creative_provider_routing.py`:

```python
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional


CREATIVE_AGENT_IDS = {
    "ugc_media_agent",
    "ugc_creative_agent",
    "product_image_agent",
    "ad_creative_agent",
    "creative_rotation_agent",
    "social_media_content_agent",
    "ads_optimisation_agent",
}

CREATIVE_AGENT_ALIASES = {
    "paid_ads_agent": "ads_optimisation_agent",
    "social_media_manager_content_creator_agent": "social_media_content_agent",
    "product_video_agent": "ugc_media_agent",
    "product_visual_agent": "product_image_agent",
    "campaign_creative_agent": "ad_creative_agent",
}

VIDEO_MODELS_BY_QUALITY = {
    "720p": {
        "provider": "higgsfield",
        "model": "Kling 3.0 Turbo",
        "quality": "720p",
        "capability": "video_generation",
    },
    "1080p": {
        "provider": "higgsfield",
        "model": "Kling 3.0",
        "quality": "1080p",
        "capability": "video_generation",
    },
    "4k": {
        "provider": "higgsfield",
        "model": "Cinema Studio 4K",
        "quality": "4K",
        "capability": "video_generation",
    },
}

IMAGE_MODELS_BY_TIER = {
    "standard": {
        "provider": "nano_banana",
        "model": "Nano Banana 2",
        "tier": "standard",
        "capability": "image_generation",
    },
    "production": {
        "provider": "nano_banana",
        "model": "Nano Banana 2",
        "tier": "production",
        "capability": "image_generation",
    },
    "premium": {
        "provider": "nano_banana",
        "model": "Nano Banana Pro",
        "tier": "premium",
        "capability": "image_generation",
    },
    "pro": {
        "provider": "nano_banana",
        "model": "Nano Banana Pro",
        "tier": "pro",
        "capability": "image_generation",
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_creative_agent_id(agent_id: str) -> str:
    raw = str(agent_id or "").strip()
    return CREATIVE_AGENT_ALIASES.get(raw, raw)


def is_creative_agent(agent_id: str) -> bool:
    return normalize_creative_agent_id(agent_id) in CREATIVE_AGENT_IDS


def normalize_video_quality(value: Any) -> str:
    raw = str(value or "").strip().lower().replace(" ", "")
    if raw in {"720", "720p", "hd"}:
        return "720p"
    if raw in {"4k", "2160", "2160p", "uhd"}:
        return "4k"
    return "1080p"


def normalize_image_tier(value: Any) -> str:
    raw = str(value or "").strip().lower().replace(" ", "_")
    if raw in {"premium", "pro", "professional", "high_end"}:
        return "premium" if raw != "pro" else "pro"
    if raw in {"production", "prod"}:
        return "production"
    return "standard"


def _media_types(media_type: str) -> set[str]:
    raw = str(media_type or "both").strip().lower()
    if raw in {"video", "image"}:
        return {raw}
    if raw in {"both", "media", "creative", "video_image", "image_video"}:
        return {"video", "image"}
    return set()


def _context_value(request_context: Optional[Dict[str, Any]], *keys: str) -> Any:
    context = request_context or {}
    media_request = context.get("media_request") if isinstance(context.get("media_request"), dict) else {}
    for key in keys:
        if key in context and context[key] not in (None, ""):
            return context[key]
        if key in media_request and media_request[key] not in (None, ""):
            return media_request[key]
    return ""


def resolve_creative_provider_route(
    agent_id: str,
    media_type: str = "both",
    video_quality: str = "",
    image_tier: str = "",
    request_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    canonical_agent_id = normalize_creative_agent_id(agent_id)
    if canonical_agent_id not in CREATIVE_AGENT_IDS:
        return {
            "success": False,
            "agent_id": agent_id,
            "canonical_agent_id": canonical_agent_id,
            "reason": "unknown_creative_agent",
            "credential_values_exposed": False,
        }

    selected_media_types = _media_types(media_type or _context_value(request_context, "media_type", "type"))
    if not selected_media_types:
        return {
            "success": False,
            "agent_id": agent_id,
            "canonical_agent_id": canonical_agent_id,
            "reason": "unsupported_media_type",
            "credential_values_exposed": False,
        }

    route: Dict[str, Any] = {
        "success": True,
        "agent_id": agent_id,
        "canonical_agent_id": canonical_agent_id,
        "media_types": sorted(selected_media_types),
        "owner_governed_execution_required": True,
        "credential_values_exposed": False,
        "created_at": _now_iso(),
    }

    if "video" in selected_media_types:
        quality = normalize_video_quality(video_quality or _context_value(request_context, "video_quality", "quality"))
        route["video"] = dict(VIDEO_MODELS_BY_QUALITY[quality])

    if "image" in selected_media_types:
        tier = normalize_image_tier(image_tier or _context_value(request_context, "image_tier", "image_quality", "quality"))
        route["image"] = dict(IMAGE_MODELS_BY_TIER[tier])

    return route


def creative_provider_status() -> Dict[str, Any]:
    return {
        "success": True,
        "creative_agent_ids": sorted(CREATIVE_AGENT_IDS),
        "aliases": dict(CREATIVE_AGENT_ALIASES),
        "providers": {
            "higgsfield": {
                "display_name": "Higgsfield",
                "capabilities": ["video_generation"],
                "models": ["Kling 3.0 Turbo", "Kling 3.0", "Cinema Studio 4K"],
                "credential_values_exposed": False,
            },
            "nano_banana": {
                "display_name": "Nano Banana",
                "capabilities": ["image_generation"],
                "models": ["Nano Banana 2", "Nano Banana Pro"],
                "credential_values_exposed": False,
            },
        },
        "credential_values_exposed": False,
        "created_at": _now_iso(),
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run from repo root:

```bash
cd backend
pytest tests/test_creative_provider_routing.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/runtime/creative_provider_routing.py backend/tests/test_creative_provider_routing.py
git commit -m "Add creative provider routing contract"
```

---

### Task 2: Provider Stack and Status Metadata

**Files:**
- Modify: `backend/app/runtime/audio_visual_provider_stack.py`
- Test: `backend/tests/test_creative_provider_routing.py`

**Interfaces:**
- Consumes: `CREATIVE_AGENT_IDS`, `creative_provider_status()`, `provider_config_status(provider_key: str) -> dict`, `providers_for_agent(agent_id: str) -> list[str]`, `recommended_stack_for_task(agent_id: str, task: str = "") -> dict`
- Produces: provider stack entries for `higgsfield` and `nano_banana`

- [ ] **Step 1: Add failing provider stack tests**

Append to `backend/tests/test_creative_provider_routing.py`:

```python
from app.runtime.audio_visual_provider_stack import (
    full_provider_stack_status,
    provider_config_status,
    providers_for_agent,
    recommended_stack_for_task,
)


def test_provider_stack_exposes_higgsfield_and_nano_banana():
    status = full_provider_stack_status()

    assert "higgsfield" in status["providers"]
    assert "nano_banana" in status["providers"]
    assert status["providers"]["higgsfield"]["models"] == [
        "Kling 3.0 Turbo",
        "Kling 3.0",
        "Cinema Studio 4K",
    ]
    assert status["providers"]["nano_banana"]["models"] == [
        "Nano Banana 2",
        "Nano Banana Pro",
    ]
    assert status["credential_values_exposed"] is False


@pytest.mark.parametrize("agent_id", CREATIVE_AGENT_CASES)
def test_provider_stack_gives_creative_agents_higgsfield_and_nano_banana(agent_id):
    providers = providers_for_agent(agent_id)

    assert "higgsfield" in providers
    assert "nano_banana" in providers


def test_recommended_stack_prioritizes_higgsfield_for_video_and_nano_banana_for_image():
    video_stack = recommended_stack_for_task("ugc_media_agent", "Create a 720p product video")
    image_stack = recommended_stack_for_task("product_image_agent", "Create a premium product image")

    assert video_stack["recommended_order"][0] == "higgsfield"
    assert image_stack["recommended_order"][0] == "nano_banana"


def test_provider_config_status_keeps_credentials_hidden():
    status = provider_config_status("higgsfield")

    assert status["provider"] == "higgsfield"
    assert "credential_values_exposed" in status
    assert status["credential_values_exposed"] is False
    assert "api_key" not in str(status).lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cd backend
pytest tests/test_creative_provider_routing.py -q
```

Expected: FAIL because `higgsfield` and `nano_banana` are not in `PROVIDER_STACK` and provider status does not expose `models`.

- [ ] **Step 3: Update provider stack metadata**

Modify `backend/app/runtime/audio_visual_provider_stack.py`:

```python
from app.runtime.creative_provider_routing import (
    CREATIVE_AGENT_IDS,
    creative_provider_status,
)
```

Add these entries to `PROVIDER_STACK`:

```python
    "higgsfield": {
        "category": ["video", "text_to_video", "image_to_video", "creative_motion"],
        "env_keys": ["HIGGSFIELD_API_KEY"],
        "agents": sorted(CREATIVE_AGENT_IDS),
        "live_call_enabled_env": "HIGGSFIELD_LIVE_EXECUTION_ENABLED",
        "models": ["Kling 3.0 Turbo", "Kling 3.0", "Cinema Studio 4K"],
    },
    "nano_banana": {
        "category": ["image", "product_image", "ad_creative_image"],
        "env_keys": ["NANO_BANANA_API_KEY"],
        "agents": sorted(CREATIVE_AGENT_IDS),
        "live_call_enabled_env": "NANO_BANANA_LIVE_EXECUTION_ENABLED",
        "models": ["Nano Banana 2", "Nano Banana Pro"],
    },
```

Update `provider_config_status()` so the returned dict includes:

```python
        "models": provider.get("models", []),
```

Update `full_provider_stack_status()` so the returned dict includes:

```python
        "creative_provider_routing": creative_provider_status(),
```

Update `recommended_stack_for_task()` preferred ordering:

```python
    if "video" in task_lower or "ugc" in task_lower or "reel" in task_lower:
        preferred.extend(["higgsfield", "kling", "runway", "heygen"])
    if "image" in task_lower or "product photo" in task_lower or "visual" in task_lower:
        preferred.extend(["nano_banana", "openai", "replicate"])
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```bash
cd backend
pytest tests/test_creative_provider_routing.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/runtime/audio_visual_provider_stack.py backend/tests/test_creative_provider_routing.py
git commit -m "Expose creative provider stack metadata"
```

---

### Task 3: Admin and Worker Routing Integration

**Files:**
- Modify: `backend/app/routes/admin.py`
- Modify: `backend/app/agents/agent_worker.py`
- Modify: `backend/app/integrations/execution_adapters.py`
- Test: `backend/tests/test_creative_provider_routing.py`

**Interfaces:**
- Consumes: `is_creative_agent(agent_id: str) -> bool`
- Consumes: `resolve_creative_provider_route(...) -> dict`
- Produces: `context["creative_provider_route"]`
- Produces: adapter result payload keys `selected_video_provider`, `selected_video_model`, `selected_image_provider`, `selected_image_model`

- [ ] **Step 1: Add failing integration-focused tests**

Append to `backend/tests/test_creative_provider_routing.py`:

```python
from app.integrations.execution_adapters import ExecutionAdapters


def test_execution_adapter_preserves_selected_creative_models_without_credentials():
    adapter = ExecutionAdapters(db=None)
    route = resolve_creative_provider_route(
        agent_id="ugc_media_agent",
        media_type="both",
        video_quality="4K",
        image_tier="pro",
    )

    result = adapter.execute(
        adapter_name="ugc_video_provider_adapter",
        payload={
            "workflow": {
                "tenant_id": "workspace-test",
                "task": "Create a cinematic product launch clip",
                "creative_provider_route": route,
            },
            "context": {
                "agent_id": "ugc_media_agent",
                "job_id": "job-test",
                "creative_provider_route": route,
            },
        },
    )

    assert result.execution_payload["selected_video_provider"] == "higgsfield"
    assert result.execution_payload["selected_video_model"] == "Cinema Studio 4K"
    assert result.execution_payload["selected_image_provider"] == "nano_banana"
    assert result.execution_payload["selected_image_model"] == "Nano Banana Pro"
    assert result.provider_ready is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cd backend
pytest tests/test_creative_provider_routing.py::test_execution_adapter_preserves_selected_creative_models_without_credentials -q
```

Expected: FAIL because the adapter does not yet copy selected provider/model metadata into `execution_payload`.

- [ ] **Step 3: Enrich admin run context**

In `backend/app/routes/admin.py`, inside `admin_run_agent()` after `norm_id` validation and before creating `AgentJob`, add:

```python
    from app.runtime.creative_provider_routing import (
        is_creative_agent,
        resolve_creative_provider_route,
    )

    run_context = dict(body.context or {})
    if is_creative_agent(norm_id):
        media_request = run_context.get("media_request") if isinstance(run_context.get("media_request"), dict) else {}
        route_media_type = media_request.get("media_type") or media_request.get("type") or run_context.get("media_type") or "both"
        run_context["creative_provider_route"] = resolve_creative_provider_route(
            agent_id=norm_id,
            media_type=route_media_type,
            video_quality=media_request.get("video_quality") or run_context.get("video_quality") or "",
            image_tier=media_request.get("image_tier") or run_context.get("image_tier") or "",
            request_context=run_context,
        )
```

Then change the `AgentJob` creation input line from:

```python
        input_data=_json.dumps({"prompt": body.prompt[:10_000], "context": body.context}),
```

to:

```python
        input_data=_json.dumps({"prompt": body.prompt[:10_000], "context": run_context}),
```

- [ ] **Step 4: Route all creative agents in the worker**

In `backend/app/agents/agent_worker.py`, import inside the provider-routing section:

```python
                from app.runtime.creative_provider_routing import is_creative_agent, resolve_creative_provider_route
```

Replace:

```python
        if job.agent_id == "ugc_media_agent":
```

with:

```python
        if is_creative_agent(job.agent_id):
```

Before `adapter_result = adapters.execute(...)`, add:

```python
                creative_provider_route = context.get("creative_provider_route")
                if not isinstance(creative_provider_route, dict) or not creative_provider_route.get("success"):
                    creative_provider_route = resolve_creative_provider_route(
                        agent_id=job.agent_id,
                        media_type="both",
                        request_context=context,
                    )
```

Add `creative_provider_route` into both `workflow` and `context` payloads passed to the adapter:

```python
                            "creative_provider_route": creative_provider_route,
```

Pass the selected video model into Higgsfield execution:

```python
                                model=creative_provider_route.get("video", {}).get("model"),
```

- [ ] **Step 5: Preserve selected models in the adapter**

In `backend/app/integrations/execution_adapters.py`, inside `_ugc_video_provider_adapter()`, read the route:

```python
        context = payload.get("context", {}) if isinstance(payload.get("context"), dict) else {}
        creative_provider_route = (
            workflow.get("creative_provider_route")
            if isinstance(workflow.get("creative_provider_route"), dict)
            else context.get("creative_provider_route")
        )
        video_route = creative_provider_route.get("video", {}) if isinstance(creative_provider_route, dict) else {}
        image_route = creative_provider_route.get("image", {}) if isinstance(creative_provider_route, dict) else {}
```

Add these keys to the returned `execution_payload`:

```python
                "creative_provider_route": creative_provider_route,
                "selected_video_provider": video_route.get("provider"),
                "selected_video_model": video_route.get("model"),
                "selected_image_provider": image_route.get("provider"),
                "selected_image_model": image_route.get("model"),
```

- [ ] **Step 6: Run tests to verify they pass**

Run:

```bash
cd backend
pytest tests/test_creative_provider_routing.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/app/routes/admin.py backend/app/agents/agent_worker.py backend/app/integrations/execution_adapters.py backend/tests/test_creative_provider_routing.py
git commit -m "Wire creative agents to provider routing"
```

---

### Task 4: Verification and Build

**Files:**
- Verify: `backend/app/runtime/creative_provider_routing.py`
- Verify: `backend/app/runtime/audio_visual_provider_stack.py`
- Verify: `backend/app/routes/admin.py`
- Verify: `backend/app/agents/agent_worker.py`
- Verify: `backend/app/integrations/execution_adapters.py`

**Interfaces:**
- Consumes all interfaces from Tasks 1-3.
- Produces a clean build/test result and final commit state.

- [ ] **Step 1: Run focused backend tests**

Run:

```bash
cd backend
pytest tests/test_creative_provider_routing.py tests/test_admin_providers.py -q
```

Expected: PASS.

- [ ] **Step 2: Run syntax check for touched backend files**

Run:

```bash
cd backend
python -m py_compile app/runtime/creative_provider_routing.py app/runtime/audio_visual_provider_stack.py app/routes/admin.py app/agents/agent_worker.py app/integrations/execution_adapters.py
```

Expected: no output and exit code 0.

- [ ] **Step 3: Run frontend build**

Run from repo root:

```bash
npm.cmd run build
```

Expected: build completes successfully. If the existing `frontend/tsconfig.tsbuildinfo` changes again, leave it unstaged unless the build requires committing it.

- [ ] **Step 4: Inspect final diff**

Run:

```bash
git status --short
git diff --stat
```

Expected: only intentional implementation files are modified, plus the pre-existing generated `frontend/tsconfig.tsbuildinfo` if it remains dirty.

- [ ] **Step 5: Final implementation commit if needed**

If Tasks 1-3 did not already commit all code, commit remaining intentional files:

```bash
git add backend/app/runtime/creative_provider_routing.py backend/app/runtime/audio_visual_provider_stack.py backend/app/routes/admin.py backend/app/agents/agent_worker.py backend/app/integrations/execution_adapters.py backend/tests/test_creative_provider_routing.py
git commit -m "Complete creative provider routing verification"
```

Expected: commit succeeds or there is nothing left to commit.

---

## Self-Review

- Spec coverage: the plan covers one canonical routing layer, all listed creative-capable agents, Higgsfield video model mapping, Nano Banana image model mapping, provider status metadata, admin context enrichment, worker routing, adapter metadata, and tests.
- Placeholder scan: no unresolved implementation placeholders are present; each task includes exact file paths, code snippets, commands, and expected results.
- Type consistency: `resolve_creative_provider_route()` returns dict keys consumed consistently by provider stack, admin route, worker route, and execution adapter.
