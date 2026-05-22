# Premium Media Provider Workflow Plan

## Purpose

Define how high-end media assets will be produced, reviewed, stored, and reused before any provider API integration is added.

## Current rule

No backend/runtime/architecture changes yet.

This stage is manual/provider-assisted asset production only.

## Recommended provider workflow

### 1. Landing page hero / cinematic product visuals

Primary options:

- Spline for interactive 3D hero scenes
- Runway for cinematic WebM/MP4 hero loops
- Luma/Pika/Kling-style tools for short premium motion loops
- OpenAI image generation for high-quality static hero frames/posters

Output files:

- `/frontend/public/media/landing/hero/hero-command-centre.webm`
- `/frontend/public/media/landing/hero/hero-command-centre.mp4`
- `/frontend/public/media/landing/hero/hero-command-centre-poster.webp`
- `/frontend/public/media/lottie/agent-orbit-network.json`

### 2. UGC video/avatar assets

Primary options:

- ElevenLabs/OpenAI voice for voice previews
- Runway/Pika/Luma-style tools for video scenes
- AI avatar/video platforms for realistic creator-style UGC clips
- OpenAI image generation for avatar concept frames and scene references

Output folders:

- `/frontend/public/media/ugc/avatars`
- `/frontend/public/media/ugc/scenes`
- `/frontend/public/media/ugc/voice-previews`

### 3. Ad creative/image assets

Primary options:

- OpenAI image generation for ad visual concepts
- Midjourney/manual export workflow for high-end brand visuals
- Krea/Leonardo-style workflows for product/lifestyle variations
- Canva/Figma/After Effects/manual tools for templates

Output folders:

- `/frontend/public/media/ads/backgrounds`
- `/frontend/public/media/ads/templates`
- `/frontend/public/media/product-images/mockups`
- `/frontend/public/media/product-images/lifestyle`

### 4. Audio/music

Primary options:

- ElevenLabs/OpenAI/Cartesia-style voice generation
- licensed music beds
- generated music beds
- sound design packs

Output folders:

- `/frontend/public/media/audio/voice-packs`
- `/frontend/public/media/audio/music-beds`

## Asset quality rules

Every production asset must pass:

- commercial quality
- mobile-safe framing
- no watermark
- no confidential client data
- reusable naming
- consistent visual identity
- compressed production format
- accessible fallback if animation fails

## Owner approval rule

Paid generation, paid stock assets, paid subscriptions, and campaign-scale media production require owner approval before purchase/spend.

## Integration order

1. Produce first landing hero poster image.
2. Produce first hero WebM/MP4 loop.
3. Add files to the correct public media slots.
4. Wire landing page to `PremiumHeroMedia`.
5. Test desktop/mobile.
6. Only then add UGC/avatar/audio production samples.
7. Only after manual workflow is proven, consider provider API integration.

## Provider API integration later

Do not connect provider APIs until the manual asset workflow is proven.

When added later, provider API integration must include:

- owner spending approval
- secret storage outside repo
- audit logs
- tenant-safe outputs
- provider failure fallback
- no direct client access to raw provider credentials
