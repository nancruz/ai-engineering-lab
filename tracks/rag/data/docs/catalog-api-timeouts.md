---
id: catalog-api-timeouts
title: Catalog API timeouts and retries
service: catalog
type: standard
status: current
updated: 2026-05-20
access: all
---
# Catalog API timeouts and retries

Every caller of `catalog-api` must use the same deadline and retry rules. Inconsistent timeouts caused the 2025 home-screen outage, when slow callers held connections open for seconds.

## Deadline

Catalog requests use an 800 ms total deadline in production. Set it with:

```
CATALOG_DEADLINE_MS=800
```

The deadline covers the whole request, including any retry. A retry never gets a fresh 800 ms.

## Retries

- Idempotent reads (`GET`) may be retried once, and only if time remains inside the original deadline.
- Writes (`POST`, `PUT`, `DELETE`) are never retried automatically. Return the error to the caller.
- Use jittered backoff between 20 and 50 ms before the retry.

## Circuit breaker

The client opens its circuit breaker when 50% of requests fail across a window of 20 requests within 10 seconds. While open, calls fail fast with `CATALOG_UNAVAILABLE`. After 30 seconds the breaker goes half-open and lets one request through to test recovery.

## Fallbacks

The home screen shows the cached rail from the last successful response when the catalog is unavailable. Search shows an error state instead of stale results, because stale search results confuse users more than an error does.
