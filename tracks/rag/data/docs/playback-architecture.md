---
id: playback-architecture
title: Playback architecture overview
service: playback
type: architecture
status: current
updated: 2026-07-30
access: all
---
# Playback architecture overview

This page gives new engineers a map of what happens between pressing play and the first frame. Each component has its own runbook; this page links them together but does not repeat their procedures.

## Components

- **Player apps** (web, TV, mobile) fetch a manifest, request a DRM license and download video segments. They report failures as `PLAY-xxxx` error codes.
- **playback-api** decides which manifest and which CDN to use for a session, based on the user's region, device and subscription.
- **License service** checks entitlement and issues DRM licenses.
- **CDN** serves video segments from edge locations close to the viewer. The origin holds the packaged files.
- **catalog-api** provides titles, artwork and availability windows to the apps and to playback-api.

## Releases

playback-api is released several times a week through the standard deploy pipeline with canary stages. When a release misbehaves, the playback rollback runbook describes how to restore the previous one. Releases are never patched in place.

## Observability

Each playback session gets a session ID that appears in player logs, API traces and CDN logs. The playback dashboard shows start-up time, rebuffering ratio and error ratio per region and device family. Start-up time above 3 seconds at p90 is the main quality alert.

## Capacity

playback-api autoscales on CPU and request rate. Large live events are prepared separately; see the live events playbook.
