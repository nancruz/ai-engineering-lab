---
id: postmortem-2026-07-catalog-cache-stampede
title: "Postmortem: catalog cache stampede (July 2026)"
service: catalog
type: postmortem
status: current
updated: 2026-07-09
access: all
---
# Postmortem: catalog cache stampede (July 2026)

Severity: SEV2. Duration: 32 minutes. Date: 2 July 2026.

## Summary

A routine deploy of `catalog-api` flushed the entire response cache. Thousands of identical requests then went to the database at the same time, a thundering herd. Catalog p99 latency rose from 180 ms to 4.2 seconds and the home screen showed empty rails for many users.

## Root cause

The deploy script ran `cache flush --all` as a post-deploy step. That step was meant for staging only and had been copied into the production pipeline. All entries also had the same 300-second TTL, so after the first refill they expired together again, producing a second, smaller spike.

## Fixes

- Request coalescing: concurrent misses for the same key wait for a single database read.
- Jittered TTL: entries now expire after 300 seconds plus or minus 10%, so they do not expire together.
- The post-deploy flush step was removed from the production pipeline.

## Guidance for engineers

Never flush the entire catalog cache in production. Invalidate only the affected keys:

`lumenctl cache invalidate catalog --prefix title:12345`

If a large invalidation is unavoidable, do it in batches and watch the database load dashboard between batches.
