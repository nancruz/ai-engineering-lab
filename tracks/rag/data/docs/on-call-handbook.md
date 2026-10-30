---
id: on-call-handbook
title: On-call handbook
service: all
type: handbook
status: current
updated: 2026-04-03
access: all
---
# On-call handbook

Every product engineering team runs a weekly on-call rotation with a primary and a secondary engineer. This handbook explains what is expected, what tooling you need and how to hand over.

## Before your first shift

- Shadow at least one full week with an experienced primary.
- Check you can log in to the pager app, the VPN, the observability stack and the release registry.
- Read the runbooks for your team's services and the incident severity levels.
- Make sure your laptop is charged and you have a working mobile connection when you are away from home.

## The rotation

Shifts last one week. Handover happens every Monday at 10:00 UTC in a 15-minute call between the outgoing and incoming primary. The secondary joins when there is an ongoing incident.

You can swap shifts with a teammate. Update the rotation in the pager app yourself; a swap agreed in chat only does not count.

## Responding to pages

- Acknowledge SEV1 and SEV2 pages within 5 minutes.
- If the primary does not acknowledge within 10 minutes, the page escalates to the secondary automatically. After another 10 minutes it escalates to the engineering manager.
- SEV3 pages outside working hours can wait until 09:00 local time. Acknowledge them so they stop escalating, then snooze.

Acknowledging a page means you own it until you hand it to someone else explicitly. Write in the incident channel what you are looking at, even if it is only "investigating".

## During an incident

The first responder is the incident commander until someone else takes the role. The incident commander coordinates and decides; they should not also be the person typing commands. For SEV1, ask for a dedicated incident commander from the incident commander rota as soon as possible.

Keep a timeline in the incident channel: what you saw, what you changed and when. It makes the postmortem much easier.

## Handover checklist

1. Open incidents and their current owner.
2. Alerts that fired more than twice during the week, and whether they need tuning.
3. Pending rollbacks, blocked releases and active feature-flag kill switches.
4. Anything you promised to follow up on.

## Looking after yourself

If you were paged between 00:00 and 06:00, start late the next day. If a shift was very heavy, tell your manager; heavy weeks are a signal that alerts or services need work, not that you need to try harder.
