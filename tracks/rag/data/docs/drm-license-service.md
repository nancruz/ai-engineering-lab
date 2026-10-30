---
id: drm-license-service
title: DRM license service overview
service: drm
type: architecture
status: current
updated: 2026-06-30
access: all
---
# DRM license service overview

The license service issues decryption licenses that let a player play protected content. It supports Widevine, FairPlay and PlayReady.

## Request flow

1. The player fetches the manifest and finds the content key ID.
2. The player sends a license request to `license.lumen.internal` with the key ID and a session token.
3. The service checks entitlement: is the account subscribed, and is the title available in the account's region?
4. If both checks pass, the service returns a license. If entitlement fails, it returns an error that the player shows as `PLAY-2003`.

## License durations

- Streaming licenses last 2 hours and are renewed silently while the user keeps watching.
- Offline download licenses last 30 days, and 48 hours once playback has started.

## Device clocks

Licenses carry start and expiry times. If a device clock is more than 5 minutes wrong, validation fails on the device and the player reports `PLAY-4012`.

## Operations

The service runs in three regions with active-active routing. It must answer within 300 ms at p99; slower answers show up in players as `PLAY-2007` timeouts.
