# DIREM-018 — Post-release Backlog Planning

## Status
Implemented

## Version target
`DIREM post-v0.1.0`

## Workstream
Docs / Release

## Recommended branch
`docs/DIREM-018-post-release-backlog-planning`

## Owner / Contributors

Project Owner:
- 1D1L1R

Contributors for this ticket:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — docs/release planning executor

## Purpose

Plan DIREM development after `direm-v0.1.0`.

DIREM v0.1.0 Core MVP is released. This ticket should organize the next backlog into clear version lanes without implementing any new product behavior.

## Current state

Released:

- `direm-v0.1.0` — Core MVP

Implemented:

- Telegram bot commands
- reminder creation/list/control/delete
- worker delivery MVP
- ru/kk/en language selection
- command menu
- cancel/help reply keyboard
- inline reminder control buttons
- runtime smoke checklist

Known limitations:

- no guided onboarding
- no timezone picker
- no delivery history command
- no retry scheduler
- no reminder editing
- no dashboard
- no webhook mode
- no AI translation
- no web UI

## Scope

In scope:

- update `docs/ROADMAP.md`;
- optionally add `docs/BACKLOG.md` if useful;
- split next work into version lanes:
  - `v0.1.1` polish / UX / small fixes;
  - `v0.2.0` functional expansion;
  - parked / later;
- define recommended next 5–8 tickets;
- identify release-blocking vs nice-to-have work;
- keep roadmap honest and non-promissory;
- update `docs/DECISIONS.md` only if a real decision is made;
- do not change application code.

Suggested next lanes:

### v0.1.1 — UX polish

- Guided first-run onboarding
- Timezone picker UX
- Kazakh/Russian/English copy polish
- Better empty states and quick actions
- Maybe command/help text polish after real usage

### v0.2.0 — Reminder power features

- Delivery history command
- Retry policy MVP
- Reminder editing
- Reminder details view
- Safer worker observability

### Parked / later

- Dashboard
- Webhook mode
- Redis/Celery
- AI translation
- Web UI
- Voice/audio features

## Out of scope

Do not implement:

- new bot commands;
- migrations;
- worker changes;
- onboarding code;
- timezone picker code;
- retries;
- dashboard/webhook;
- AI features;
- web UI.

## README update

README should not change unless it contains stale roadmap wording.

## CHANGELOG update

No CHANGELOG update required unless existing release docs are corrected.

## Acceptance criteria

- post-release roadmap is clear;
- next tickets are named and ordered;
- v0.1.1 / v0.2.0 / parked split is understandable;
- no code changes;
- no false promises;
- no release tag changes;
- no DI-CODE local reference docs committed.

## Verification commands

```bash
git status
git diff

If docs-only changes are made, automated Python checks are optional but not required unless code changed.

Implementation guard
Implement only post-release planning docs.
Do not implement product features.
Do not modify source code.
Do not create release tag.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
Keep roadmap honest: planned means planned, not implemented.
Expected result summary

After this ticket:

DIREM has a clean post-v0.1.0 roadmap;
next tickets are ready to be cut;
development can continue without collapsing all future ideas into one branch.
