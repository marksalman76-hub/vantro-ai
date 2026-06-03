# Sync Live Lip-Sync/Dubbing Adapter

## Purpose

This adapter enables controlled live Sync lip-sync/dubbing quality tests.

## Safety Rules

- Live execution only runs when `allow_live_execution=True`.
- API keys are loaded from `.env.local` or environment variables.
- Credential values are never returned.
- Metadata is saved locally under `runtime_outputs/sync_lipsync_quality_tests`.
- Client auto-execution is not enabled by this adapter.
- Paid provider usage remains owner-controlled.

## API

- Base URL: `https://api.sync.so`
- Create generation: `POST /v2/generate`
- Auth header: `x-api-key`
- Default model: `sync-3`

## Status

SYNC_LIVE_LIPSYNC_ADAPTER_READY
