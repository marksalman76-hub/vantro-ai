# HeyGen Live Avatar Video Quality Adapter

## Purpose

This adapter enables controlled live HeyGen Video Agent / avatar-video quality tests.

It is intended for owner/admin creative quality evaluation before broad customer-facing provider activation.

## Safety Rules

- Live execution only runs when `allow_live_execution=True`.
- API keys are loaded from `.env.local` or environment variables.
- Credential values are never returned.
- Metadata is saved locally under `runtime_outputs/heygen_quality_tests`.
- Client auto-execution is not enabled by this adapter.
- Paid provider usage remains owner-controlled.

## Default API Path

- Create Video Agent task: `POST https://api.heygen.com/v3/video-agents`
- Authentication header: `X-Api-Key`

## Status

HEYGEN_LIVE_AVATAR_VIDEO_ADAPTER_READY
