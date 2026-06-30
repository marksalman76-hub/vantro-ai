# Creative Provider Routing Design

Date: 2026-06-29

## Goal

Create one canonical creative provider routing layer for Vantro so every creative-capable agent can resolve the correct Higgsfield video model or Nano Banana image model before media execution begins.

This design prevents the current split where some creative flows only create briefs, some queue placeholder media jobs, and only `ugc_media_agent` has a narrow Higgsfield path.

## Scope

Creative-capable agents must include the canonical agent IDs and known aliases currently used across the app:

- `ugc_media_agent`
- `ugc_creative_agent`
- `product_image_agent`
- `ad_creative_agent`
- `creative_rotation_agent`
- `social_media_content_agent`
- `ads_optimisation_agent`

The routing layer should also support future creative agents by allowing the agent registry/provider metadata to opt them into the same capability set.

## Provider Model Rules

Video routing must select Higgsfield with a model based on requested quality:

- `720p` routes to `Kling 3.0 Turbo`
- `1080p` routes to `Kling 3.0`
- `4K` routes to `Cinema Studio 4K`

Image routing must select Nano Banana based on requested image quality/tier:

- Standard or production image requests route to `Nano Banana 2`
- Premium or pro image requests route to `Nano Banana Pro`

Unknown or missing video quality should default to `1080p` and therefore `Kling 3.0`. Unknown or missing image tier should default to standard and therefore `Nano Banana 2`.

## Architecture

Add a canonical backend routing module responsible for:

- normalizing creative agent IDs and aliases
- identifying whether a request needs video, image, or both
- normalizing video quality and image tier values from admin/client request context
- returning provider, model, media type, capability, and governance metadata
- exposing a provider status summary without exposing credentials

Existing provider metadata should reference this routing layer rather than duplicating lists of providers and agents.

## Data Flow

Admin Create Media:

1. The admin UI collects media type, aspect ratio, platform, tone, video quality, and brand/reference assets.
2. The UI sends request context to the backend agent run endpoint.
3. The backend resolves the selected creative agent through the canonical routing layer.
4. The routing layer attaches video/image provider choices to the job context.
5. The worker/execution adapter uses those choices when invoking a live provider path.

Agent Execution:

1. Any creative-capable agent can request a creative provider plan.
2. Aliases resolve to canonical creative capabilities instead of being blocked by mismatched IDs.
3. Provider execution remains owner-governed and credential-safe.
4. If credentials or live execution are unavailable, the job should return a clear provider-not-ready result rather than silently falling back to a completed brief.

## Backend Integration Points

The implementation should update:

- provider stack/status metadata
- creative/media routing selection
- admin create-media request context handling
- tests covering all creative-capable agents and model selection

The first implementation should not depend on local Claude Code MCP authentication. Claude Code Higgsfield MCP is useful for local operator workflows, but the deployed Vantro backend needs its own deployable execution surface through credentials, API, or a server-side MCP/CLI bridge.

## Error Handling

Provider routing must distinguish:

- unknown creative agent
- unsupported media type
- provider credentials missing
- live execution disabled
- owner approval required
- provider execution failure

Credential values must never be logged, returned, or stored in generated artifacts.

## Testing

Add focused tests proving:

- every video-capable creative agent resolves to the Higgsfield video models allowed for that agent and package tier
- every image-capable creative agent resolves to the Nano Banana image models allowed for that agent and package tier
- `720p`, `1080p`, and `4K` select the exact requested Higgsfield models
- standard/production image requests select `Nano Banana 2`
- premium/pro image requests select `Nano Banana Pro`
- alias IDs resolve consistently to canonical creative routing
- missing quality values use the documented defaults
- restricted agents and restricted packages return clear entitlement failures

## Agent And Package Entitlements

Creative provider access is intentionally tiered because Vantro sells agents both as a team and as separate purchasable agents. The routing layer must intersect:

- the selected agent's model policy
- the workspace package tier
- owner/admin package override, when applicable
- provider readiness

Lower-tier creative agents must not silently access premium generation software. For example, `social_media_content_agent` and `creative_rotation_agent` are limited to fast lower-cost generation (`Kling 3.0 Turbo` and `Nano Banana 2`), while `ugc_creative_agent` can access premium models such as `Cinema Studio 4K` and `Nano Banana Pro` when the package tier allows it.

The current policy source of truth is:

`backend/app/runtime/creative_agent_capability_policy.py`

Expected entitlement failure reasons include:

- `media_type_not_allowed_for_agent`
- `media_type_not_allowed_for_package`
- `model_not_allowed_for_agent`
- `model_not_allowed_for_package`

## Non-Goals

This design does not directly deploy live paid provider execution by itself. It creates the canonical routing contract that live provider adapters can consume safely.

This design does not store or expose Higgsfield, Kling, or Nano Banana secrets.

This design does not remove existing governance, approval, credit, or package checks.

## Acceptance Criteria

- There is one source of truth for creative provider routing.
- Every listed creative agent and alias can resolve only the video and image provider choices it is entitled to use.
- Admin create-media jobs include the selected provider/model in backend context.
- Provider status surfaces the new Higgsfield and Nano Banana capabilities without exposing secrets.
- Tests prove the quality-to-model mapping, creative-agent coverage, and entitlement failures.
