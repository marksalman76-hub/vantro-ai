# Admin Creative Media Asset Viewer

## Purpose

This layer exposes generated creative media asset records for admin visibility.

## Supported Assets

- ElevenLabs audio files
- Runway video files
- HeyGen metadata records
- Kling video files
- Sync lip-sync output files

## Safety Rules

- Credential values are never exposed.
- The route only reads local generated media records.
- The route does not trigger provider calls.
- The route does not perform external actions.
- Customer-safe visibility metadata is preserved.

## Status

ADMIN_CREATIVE_MEDIA_ASSET_VIEWER_READY
