# Creative Provider Credential Activation Checks

## Purpose

This layer validates premium creative provider credential readiness without enabling uncontrolled live execution.

## Covered Provider Categories

- Runway-style video
- Kling-style cinematic video
- HeyGen-style avatar video
- ElevenLabs-style premium voice
- Lip-sync and dubbing
- Music/SFX generation
- Image/video upscaling

## Important Rules

- Credential presence does not enable live execution.
- Live provider execution requires explicit owner approval.
- Credential values must never be exposed.
- Paid provider usage remains owner-approved.
- Provider execution must remain auditable and governed.
- Tenant isolation and customer-safe visibility must remain preserved.

## Status

CREATIVE_PROVIDER_CREDENTIAL_ACTIVATION_CHECKS_READY
