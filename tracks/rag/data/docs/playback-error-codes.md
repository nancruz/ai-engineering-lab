---
id: playback-error-codes
title: Playback error codes
service: playback
type: reference
status: current
updated: 2026-08-01
access: all
---
# Playback error codes

Players report errors as `PLAY-xxxx`. The first digit tells you which layer failed: 1 manifest, 2 DRM, 3 CDN, 4 device, 5 unknown.

## Manifest errors

| Code | Meaning | What to do |
| --- | --- | --- |
| PLAY-1001 | Manifest not found (404 from origin) | Check that the title is published in the region. |
| PLAY-1004 | Manifest could not be parsed | Re-run packaging for the title; report it to the media pipeline team. |

## DRM errors

| Code | Meaning | What to do |
| --- | --- | --- |
| PLAY-2003 | License denied | The account has no entitlement for this title or region. Check the subscription and the title's rights window. |
| PLAY-2007 | License server timeout | Check the license service status. The player retries twice on its own. |

## CDN errors

| Code | Meaning | What to do |
| --- | --- | --- |
| PLAY-3002 | Segment request returned 5xx | Check the CDN status page and the edge dashboard for the user's region. |

## Device errors

| Code | Meaning | What to do |
| --- | --- | --- |
| PLAY-4012 | Device clock skew larger than 5 minutes | License validation fails when the clock is wrong. Ask the customer to turn on automatic date and time. |
| PLAY-4019 | HDCP not supported for UHD | The display cannot play 4K protected content. The player falls back to HD automatically. |

## Unknown errors

`PLAY-5000` means the player could not classify the failure. Attach the session ID to the support ticket; the playback team can look up the full trace for seven days.
