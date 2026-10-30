---
id: postmortem-2025-11-search-outage
title: "Postmortem: search outage after key revocation (November 2025)"
service: search
type: postmortem
status: current
updated: 2025-11-20
access: all
---
# Postmortem: search outage after key revocation (November 2025)

Severity: SEV2. Duration: 1 hour 25 minutes. Date: 12 November 2025.

## Summary

During a scheduled credential rotation, the old API key of `search-api` was revoked before all callers had switched to the new key. The mobile apps' backend still used the old key, so every search from mobile failed with an authentication error.

## Root cause

The rotation checklist said "migrate callers", but nobody checked the key-usage dashboard before revoking. One caller was owned by another team and had been missed.

## Fixes

- The credential rotation runbook now requires a dual-key period and a check that no traffic uses the old key before it is revoked.
- Revocation is blocked by tooling while the key-usage dashboard shows traffic on the key.
