# Runway Live Video Quality Adapter

## Purpose

This adapter enables controlled live Runway video quality tests for creative agents.

It is intended for owner/admin creative quality evaluation before broad customer-facing provider activation.

## Safety Rules

- Live execution only runs when `allow_live_execution=True`.
- API keys are loaded from `.env.local` or environment variables.
- Credential values are never returned.
- Metadata is saved locally under `runtime_outputs/runway_quality_tests`.
- Client auto-execution is not enabled by this adapter.
- Paid provider usage remains owner-controlled.
- The Runway API key must remain server-side only.

## Defaults

- `RUNWAY_MODEL=gen4.5`
- `RUNWAY_RATIO=1280:720`
- `RUNWAY_DURATION=5`

## Status

RUNWAY_LIVE_VIDEO_QUALITY_ADAPTER_READY
