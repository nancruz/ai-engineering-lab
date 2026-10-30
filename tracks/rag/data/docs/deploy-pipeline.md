---
id: deploy-pipeline
title: Deploy pipeline and freeze windows
service: all
type: standard
status: current
updated: 2026-05-02
access: all
---
# Deploy pipeline and freeze windows

All services deploy through the same pipeline. It is designed so that a bad release reaches as few users as possible.

## Stages

1. Build and unit tests.
2. Deploy to staging and run the end-to-end suite.
3. Canary at 1% of production traffic for 15 minutes.
4. Canary at 10% for 30 minutes.
5. 50%, then 100%.

## Automatic halts

The pipeline halts the rollout and pages the service on-call when, compared with the previous release:

- the error ratio rises above 2%, or
- p99 latency increases by more than 25%.

A halted rollout stays at its current percentage. The on-call decides whether to resume or to roll back using the service's rollback runbook.

## Freeze windows

No production deploys:

- on Fridays after 15:00 UTC, and at weekends;
- from 48 hours before a tier-1 live event until it ends;
- during an open SEV1 incident, except for the fix itself.

## Exceptions

An urgent fix during a freeze needs approval from the engineering director on duty. The hotfix still goes through every stage, but the canary times are halved.
