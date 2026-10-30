---
id: live-events-playbook
title: Live events playbook
service: playback
type: playbook
status: current
updated: 2026-08-18
access: all
---
# Live events playbook

Tier-1 live events, such as a football final or a season premiere broadcast live, bring up to five times the normal number of concurrent viewers in a few minutes. This playbook describes how we prepare.

## Tiers

- Tier 1: expected peak above 3 million concurrent viewers.
- Tier 2: expected peak between 500,000 and 3 million.
- Tier 3: everything else; no special preparation.

## Timeline for a tier-1 event

- 7 days before: the capacity plan is reviewed by SRE and the playback team.
- 48 hours before: deploy freeze starts for all services (see the deploy pipeline standard).
- 24 hours before: playback is pre-scaled to 3x its normal baseline. Autoscaling remains on, but it cannot scale below the pre-scaled level.
- 2 hours before: the war room opens with playback, CDN, catalog and customer support.
- During the event: the incident commander stays in the war room until the audience falls below the normal baseline.

## If capacity runs out

Do not improvise capacity changes in the war room. Emergency capacity settings exist, but they are restricted to SRE; ask the SRE on call. Meanwhile, lower the default start bitrate to reduce CDN load.

## After the event

Hold a 30-minute review within three working days, even if nothing went wrong. Record peak concurrency and the slowest component.
