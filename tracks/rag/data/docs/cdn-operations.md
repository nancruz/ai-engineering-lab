---
id: cdn-operations
title: CDN operations
service: edge
type: runbook
status: current
updated: 2026-07-21
access: all
---
# CDN operations

Lumen uses two CDN vendors, with traffic split by region. The edge team owns the configuration; any engineer may purge content for their own titles.

## Purging a title

Purge by surrogate key, which removes every segment and manifest of one title:

`lumenctl cdn purge --key title:12345`

The purge reaches all edge locations of both vendors within about a minute. Avoid full purges: they send the whole audience to the origin at once.

## Switching vendors

If one vendor has an outage, shift a region to the other vendor in the CDN console. The shift takes about five minutes because players pick the new CDN when they request the next manifest. Tell the edge on-call before shifting more than one region.

## Certificates

Edge certificates renew automatically 30 days before expiry. The edge dashboard shows days to expiry per cluster; an alert fires at 21 days.
