# Creative Quality Refinement Loop

## Purpose

This layer adds quality scoring, provider comparison, retry logic, and refinement recommendations to creative execution workflows.

## Goals

- Score creative outputs
- Compare providers
- Recommend retries
- Suggest better providers
- Improve prompts
- Generate learning signals
- Optimise future provider routing

## Example Behaviour

### Cinematic SaaS Ad

- Runway may score highest.
- Kling may be suggested as an alternative for social realism.
- Retry recommendations may appear if quality is weak.

### UGC Social Ad

- Kling may score highest.
- Runway may be suggested for premium cinematic polish.
- ElevenLabs may improve narration quality.

### Multilingual Campaign

- Sync may be recommended for localisation.
- ElevenLabs may improve multilingual narration.

## Important Rules

- Provider scoring should remain flexible.
- Learning signals can influence future routing.
- Governance cannot be overridden.
- Credentials must never be exposed.
- Live provider calls require owner approval.

## Status

CREATIVE_QUALITY_REFINEMENT_LOOP_READY
