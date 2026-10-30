---
id: catalog-api-timeouts-2023
title: Catalog API timeouts (2023)
service: catalog
type: standard
status: archived
updated: 2023-09-11
access: all
---
# Catalog API timeouts (2023)

> Archived. Superseded by the current catalog timeout standard.

Catalog requests time out after 3000 ms. Retry failed requests three times, with a fresh 3000 ms timeout for each attempt. Writes can be retried the same way as reads.
