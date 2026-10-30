---
id: search-service-runbook
title: Search service runbook
service: search
type: runbook
status: current
updated: 2026-06-05
access: all
---
# Search service runbook

`search-api` powers the search box in every app. It is separate from `catalog-api`: search queries an index of titles and people, while the catalog serves title details and rails.

## Timeouts

Search requests use a 1200 ms deadline, longer than the catalog's, because typo-tolerant queries can be slow. The apps cancel a search request when the user types another character, so most slow queries are never seen.

## Reindexing

The title index is rebuilt every night at 02:00 UTC from the catalog. A rebuild writes a new index and switches an alias when it is complete, so search keeps working during the rebuild. To rebuild by hand:

`lumenctl search reindex --wait`

## Common problems

- **New title not found**: the nightly rebuild has not run yet. Trigger a reindex.
- **Slow searches**: check the index size and the query rate on the search dashboard. A spike in one-letter queries usually comes from an app bug.
- **No results at all**: check that the index alias points to a complete index: `lumenctl search alias show`.
