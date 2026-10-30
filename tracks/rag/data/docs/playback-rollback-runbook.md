---
id: playback-rollback-runbook
title: Playback rollback runbook
service: playback
type: runbook
status: current
updated: 2026-06-12
access: all
---
# Playback rollback runbook

This runbook explains how to restore the previous release of the playback service. It replaces the 2024 version, which allowed immediate rollback without approval.

## When to roll back

Roll back production when either condition is true:

- The canary error ratio stays above 2% for 5 consecutive minutes.
- A SEV1 incident is linked to the current release.

A single error spike is not a reason to roll back. Check the canary dashboard first: short spikes during cache warm-up are expected for about two minutes after a deploy.

## Who approves

In production, the incident commander approves every rollback. If no incident is open, open one at SEV2 first, then ask the on-call incident commander. Record the approval in the incident channel before you run any command.

In staging, no approval is needed. Any engineer may restore the previous release immediately.

## Steps

1. Snapshot the diagnostic traces so the failing release can be investigated later:
   `lumenctl traces snapshot playback --release current`
2. Confirm the previous release is still healthy in the release registry:
   `lumenctl release list playback --limit 3`
3. Roll back:
   `lumenctl release rollback playback --to previous --env prod`
4. Watch the canary dashboard for 10 minutes. The error ratio should fall below 0.5%.
5. Post the outcome in the incident channel and link the trace snapshot.

The rollback shifts traffic in three steps of one third each, two minutes apart. Do not interrupt it once it has started; if it stalls, page the playback platform team.

## EU production

EU production has one extra rule. Before traffic is shifted, the data-residency check must pass:

`lumenctl compliance eu-residency-check playback --release previous`

If the check fails, do not roll back in the EU region. Keep the current release, enable the `kill.playback.new-player` flag instead and escalate to the data protection officer on duty.

## After the rollback

- Keep the failing release blocked in the registry until a fix is merged.
- Schedule a postmortem within five working days for SEV1 and SEV2 incidents.
- Delete the trace snapshot after the postmortem, and in any case within seven days, following the data retention policy.
