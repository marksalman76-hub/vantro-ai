# Creative Workflow Chaining Layer

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
