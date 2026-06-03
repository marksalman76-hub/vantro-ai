# Unified Creative Provider Orchestration

## Purpose

This layer prevents hardcoded creative workflows.

Creative agents should dynamically select the best provider mix based on creative goal, format, platform, region, language, budget, quality priority, and owner approval.

## Provider Roles

- ElevenLabs: voice, narration, accents, multilingual speech
- Runway: cinematic commercial video
- Kling: realistic/social/UGC video
- HeyGen: avatar presenter and spokesperson video
- Sync: lip-sync, dubbing, localisation

## Rules

- Do not use every provider for every job.
- Select only the providers needed for the creative goal.
- Live execution requires owner approval.
- Credentials must never be exposed.
- Provider routing should remain flexible.
- Learning scores can influence future selection.
- Governance rules cannot be overridden.

## Status

UNIFIED_CREATIVE_PROVIDER_ORCHESTRATION_READY
