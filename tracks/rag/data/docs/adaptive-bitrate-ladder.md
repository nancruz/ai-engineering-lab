---
id: adaptive-bitrate-ladder
title: Adaptive bitrate ladder
service: encoding
type: reference
status: current
updated: 2026-04-22
access: all
---
# Adaptive bitrate ladder

Every title is encoded into several renditions. The player switches between them based on available bandwidth, a technique called adaptive bitrate streaming (ABR).

## Renditions

| Rendition | Video bitrate |
| --- | --- |
| 240p | 400 kbps |
| 360p | 800 kbps |
| 480p | 1400 kbps |
| 720p | 3000 kbps |
| 1080p | 6000 kbps |
| 2160p (UHD) | 16000 kbps |

Video is cut into segments of 4 seconds. Shorter segments react faster to bandwidth changes but increase request overhead on the CDN.

## Start bitrate

The player starts at the rendition just below the bandwidth measured in the previous session on the same device. On a new device it starts at 480p.

## Data saver mode

Data saver caps playback at 480p. The player setting is `max_bitrate_kbps=1400`. UHD is also disabled when the display does not support HDCP 2.2 (see `PLAY-4019`).
