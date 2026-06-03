# ElevenLabs Live TTS Quality Adapter

## Purpose

This adapter enables controlled live ElevenLabs text-to-speech quality tests.

It is intended for owner/admin creative quality evaluation before broad customer-facing provider activation.

## Safety Rules

- Live execution only runs when `allow_live_execution=True`.
- API keys are loaded from `.env.local` or environment variables.
- Credential values are never returned.
- Generated audio is saved locally under `runtime_outputs/elevenlabs_quality_tests`.
- Client auto-execution is not enabled by this adapter.
- Paid provider usage remains owner-controlled.

## Default Provider Settings

- Default voice ID can be overridden with `ELEVENLABS_DEFAULT_VOICE_ID`.
- Default model ID can be overridden with `ELEVENLABS_MODEL_ID`.
- Default model fallback: `eleven_multilingual_v2`.

## Status

ELEVENLABS_LIVE_TTS_QUALITY_ADAPTER_READY
