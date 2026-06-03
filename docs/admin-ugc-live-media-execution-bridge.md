# Admin UGC Live Media Execution Bridge

## Purpose

This bridge routes admin UGC creative video/ad tasks into real live media execution.

## Connected Providers

- ElevenLabs for UGC voiceover generation
- Runway for UGC-style video generation

## Runtime Chain

UGC Creative Agent task
→ runtime creative execution plan
→ voice generation
→ video generation
→ local media persistence
→ admin-safe output packet

## Safety Rules

- Live execution requires owner approval.
- API keys are never exposed.
- Provider calls are explicit and auditable.
- Tenant isolation must remain preserved.
- Local generated media is saved under runtime_outputs.

## Status

ADMIN_UGC_LIVE_MEDIA_EXECUTION_BRIDGE_READY
