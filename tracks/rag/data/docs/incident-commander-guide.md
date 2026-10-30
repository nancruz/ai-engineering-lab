---
id: incident-commander-guide
title: Incident commander guide
service: all
type: guide
status: current
updated: 2026-05-11
access: all
---
# Incident commander guide

The incident commander (IC) runs the response to an incident. They coordinate people and decisions; they do not debug.

## Responsibilities

- Confirm the severity and change it if the impact changes.
- Make sure one person is investigating each lead, and that everyone knows who.
- Approve risky production actions such as rollbacks, emergency capacity and disabling features with kill switches.
- Decide when to update the status page and who writes the update.
- Declare the incident resolved and make sure a postmortem owner is named.

## Communication rhythm

Post a short update in the incident channel every 15 minutes for SEV1 and every 30 minutes for SEV2, even when there is nothing new. Silence makes people start their own parallel investigations.

## Handing over

An incident lasting more than four hours needs a fresh IC. Hand over in a call, summarise the current theory, what has been tried and what is pending, then announce the new IC in the channel.

## Becoming an IC

Engineers join the IC rota after shadowing three incidents and completing the IC workshop. The rota is separate from team on-call rotations.
