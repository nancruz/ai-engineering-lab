---
id: emergency-capacity-settings
title: Emergency capacity settings
service: playback
type: runbook
status: current
updated: 2026-08-18
access: sre
---
# Emergency capacity settings

Restricted to SRE. Do not share these values outside the SRE team.

## Playback emergency capacity

The playback emergency worker count is 720 workers. It is above the normal autoscaling maximum and costs roughly ten times the usual hourly spend, so it is a last resort.

Apply it with:

`lumenctl capacity set playback --workers 720 --reason <incident-id>`

## Limits

- Only SRE engineers may apply emergency capacity.
- It may stay in place for at most 6 hours. After that, a new approval from the SRE manager is needed.
- Return to autoscaling with `lumenctl capacity reset playback` and confirm in the incident channel.
