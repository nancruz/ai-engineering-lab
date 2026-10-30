---
id: feature-flags-policy
title: Feature flags policy
service: all
type: policy
status: current
updated: 2026-01-15
access: all
---
# Feature flags policy

Feature flags let us ship code before releasing a feature, and switch behaviour off without a deploy. Used badly, they turn into permanent hidden configuration. These rules keep them under control.

## Naming

Name release flags `team.feature.yyyy-mm`, for example `playback.new-player.2026-06`. The date is the month the flag was created, which makes old flags easy to spot.

Kill switches are long-lived flags that turn a risky component off in an emergency. Their names must start with `kill.`, for example `kill.playback.new-player`. Kill switches are exempt from the cleanup rule below.

## Lifecycle

1. Create the flag switched off in all environments.
2. Roll out by percentage in production: 1%, 10%, 50%, 100%.
3. Remove the flag and the old code path within 30 days of reaching 100%.

The flag service reports flags that have been at 100% for more than 30 days. Teams with overdue flags get a ticket automatically.

## Rules

- Flags are evaluated on the server. Apps receive the result, never the targeting rules.
- Targeting rules must not contain personal data such as e-mail addresses. Use account IDs or segments.
- Changing a flag in production counts as a production change: write it in the team channel with the reason.
