---
id: postmortem-2026-03-edge-tls-outage
title: "Postmortem: edge TLS certificate outage (March 2026)"
service: edge
type: postmortem
status: current
updated: 2026-03-21
access: all
---
# Postmortem: edge TLS certificate outage (March 2026)

Severity: SEV1. Duration: 47 minutes. Date: 14 March 2026.

## Summary

The TLS certificate on the `eu-west-2` edge cluster expired at 19:02 UTC. Browsers and TV apps in the UK and Ireland refused to connect, so playback failed for about 18% of active users in Europe. The certificate had not renewed automatically because its DNS validation record had been deleted.

## Timeline

- 18:40 — A cleanup script removes DNS records it considers unused, including the certificate's DNS validation record.
- 19:02 — The certificate expires. Error rates on the edge rise sharply.
- 19:11 — Synthetic checks alert the edge on-call. Detection took 9 minutes.
- 19:24 — The cause is identified from browser error reports (`NET::ERR_CERT_DATE_INVALID`).
- 19:41 — The validation record is restored and a new certificate is issued manually.
- 19:49 — Traffic recovers fully.

## Root cause

Automatic renewal depends on a DNS validation record. The cleanup script treated records without recent queries as unused. Validation records are only queried during renewal, so the script deleted it.

## What went well

- Rollback was not attempted; the team correctly saw that no release was involved.
- The status page was updated within 12 minutes.

## Action items

- Alert 21 days before any certificate expires, not 3 days. (Owner: edge team)
- Tag DNS validation records with `do-not-delete` and make the cleanup script skip tagged records. (Owner: platform team)
- Add certificate expiry to the edge dashboard. (Owner: edge team)
