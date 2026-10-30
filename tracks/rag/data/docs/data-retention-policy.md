---
id: data-retention-policy
title: Data retention policy
service: all
type: policy
status: current
updated: 2026-09-01
access: all
---
# Data retention policy

This policy says how long we keep each kind of data, and what must be removed before data is copied anywhere else, including search indexes and AI assistants.

## Retention periods

| Data | Kept for |
| --- | --- |
| Viewing history | 24 months, then aggregated |
| Production diagnostic traces | 7 days |
| Application logs | 30 days |
| Support tickets | 3 years |
| Payment records | as required by tax law, at least 7 years |

## Before indexing or sharing data

Remove credentials and direct customer identifiers (names, e-mail addresses, phone numbers, payment details) before any data is ingested into a search index, analytics tool or AI assistant. Replace them with internal account IDs when a link is needed.

## EU customer data

Personal data of EU customers is stored and processed in the `eu-central` region. Copying it to another region needs a reviewed data-flow assessment from the data protection officer.

## Deletion requests

Customer deletion requests are completed within 30 days. Deletion must also remove the data from caches, search indexes and backups on their normal rotation.
