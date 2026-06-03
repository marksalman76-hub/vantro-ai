# Kling Live Video Quality Adapter

## Purpose

This adapter enables controlled live Kling text-to-video quality tests for creative agents.

It is intended for owner/admin creative quality evaluation before broad customer-facing provider activation.

## Safety Rules

- Live execution only runs when `allow_live_execution=True`.
- API keys are loaded from `.env.local` or environment variables.
- Access Key and Secret Key values are never returned.
- Metadata is saved locally under `runtime_outputs/kling_quality_tests`.
- Client auto-execution is not enabled by this adapter.
- Paid provider usage remains owner-controlled.

## Defaults

- `KLING_API_BASE=https://api.klingai.com`
- `KLING_MODEL=kling-v1`
- `KLING_MODE=std`
- `KLING_ASPECT_RATIO=16:9`
- `KLING_DURATION=5`

## Status

KLING_LIVE_VIDEO_QUALITY_ADAPTER_READY
