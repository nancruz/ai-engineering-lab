---
id: incident-severity-levels
title: Incident severity levels
service: all
type: policy
status: current
updated: 2026-02-10
access: all
---
# Incident severity levels

Pick the severity from customer impact, not from how hard the fix looks. When unsure, choose the higher severity; downgrading later is cheap.

## SEV1 — critical

- Playback, sign-in or payments fail for more than 5% of active users.
- Any confirmed or suspected data breach.

Page the on-call incident commander and the service on-call immediately. Update the public status page within 15 minutes and every 30 minutes after that.

## SEV2 — major

- A whole region is degraded, or a major feature (search, downloads, profiles) is broken for many users.
- A SEV1 risk that is not customer-facing yet, for example a failing certificate renewal.

Responders join within 30 minutes. Status page updates are optional and decided by the incident commander.

## SEV3 — minor

Limited impact with a workaround, for example one device model failing to start playback. Handle it during the next business day.

## SEV4 — cosmetic

Visual or copy issues with no functional impact. Track it as a normal ticket.

## After the incident

SEV1 and SEV2 incidents need a blameless postmortem within five working days. SEV3 incidents need a short written summary in the ticket.
