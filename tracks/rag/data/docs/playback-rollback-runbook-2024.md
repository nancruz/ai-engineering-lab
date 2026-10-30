---
id: playback-rollback-runbook-2024
title: Playback rollback runbook (2024)
service: playback
type: runbook
status: archived
updated: 2024-03-02
access: all
---
# Playback rollback runbook (2024)

> Archived. Kept for historical reference only.

## When to roll back

Roll back the playback service immediately after any playback error is reported in production. Speed matters more than diagnosis.

## Who approves

No approval is required. Any developer on the playback team may roll back production or staging.

## Steps

1. Run `deployctl revert playback`.
2. Tell the team in the playback channel.

Traces do not need to be preserved; the next release will overwrite them.
