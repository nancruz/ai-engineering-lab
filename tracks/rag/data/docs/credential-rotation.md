---
id: credential-rotation
title: Rotating service credentials
service: all
type: runbook
status: current
updated: 2026-03-30
access: all
---
# Rotating service credentials

Service API keys are rotated every 90 days, and immediately if a key may have leaked. The procedure below avoids downtime because both keys are valid during the change.

## Procedure

1. Create the new key in Vault under `secret/services/<service>/api-key-next`.
2. Deploy the service with dual-key verification, so it accepts both the old and the new key.
3. Migrate every caller to the new key. Check the key-usage dashboard until no traffic uses the old key.
4. Keep both keys valid for a 24-hour overlap window, then revoke the old key.
5. Move the new key to `secret/services/<service>/api-key` and delete the `-next` entry.

## If a key has leaked

Treat it as a SEV2 incident. Run the procedure with a 1-hour overlap window instead of 24 hours and review access logs for the leaked key.

## Never

- Never paste a key or token into a ticket, chat message, document or AI assistant.
- Never revoke the old key before every caller has moved; that is how the 2025 search outage started.
