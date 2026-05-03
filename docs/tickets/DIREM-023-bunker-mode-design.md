# DIREM-023 — Bunker Mode Design

## Status
Implemented

## Version target
`DIREM v0.1.1 / v0.2.0 planning`

## Workstream
Docs / Architecture

## Recommended branch
`docs/DIREM-023-bunker-mode-design`

## Owner / Contributors

Project Owner:
- 1D1L1R

Contributors for this ticket:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — design/docs executor

## Purpose

Design Bunker Mode before implementation.

Bunker Mode is a user-level global pause feature. It should temporarily silence active reminders and later restore the user's previous reminder state.

This ticket must not implement Bunker Mode. It should define behavior, edge cases, data model direction, UX, and follow-up implementation tickets.

## Source of truth

Read before implementation:

- docs/CONCEPT.md
- docs/PRODUCT_SCOPE.md
- docs/ARCHITECTURE.md
- docs/ROADMAP.md
- docs/BACKLOG.md
- docs/DECISIONS.md
- docs/RUNTIME_SMOKE.md
- docs/tickets/DIREM-023-bunker-mode-design.md

DI-CODE reference:
- `.docs-local/DI-CODE/DI-CODE_CANON.md`
- `.docs-local/DI-CODE/DI-CODE_GITHUB_WORKFLOW.md`
- `.docs-local/DI-CODE/DI-CODE_TICKET_HANDOFF_PLAYBOOK.md`
- `.docs-local/DI-CODE/DI-CODE_COMMIT-ATTRIBUTION.md`

Important:
- Follow the active ticket first.
- Use DI-CODE_GITHUB_WORKFLOW.md for branch/commit/push rules.
- Do not stage, commit or push `.docs-local/`, `DI-CODE/`, or `docs/DI-CODE/`.

## Current state / dependencies

Assume these are accepted and merged into `main`:

- `direm-v0.1.0` — Core MVP
- DIREM-018 — post-release backlog planning
- DIREM-019 — guided first-run onboarding
- DIREM-020 — timezone picker UX
- DIREM-021 — Dorpheus copy cleanup
- DIREM-022 — Telegram main menu and hubs

Current behavior:

- reminders can be active, paused and deleted;
- worker sends due active reminders;
- paused/deleted reminders are skipped;
- user has persisted timezone and language;
- Telegram menu/hubs exist;
- no user-level global pause exists.

## Scope

### In scope

Design Bunker Mode.

Need:

- define Bunker Mode concept and exact behavior;
- decide whether Bunker is user-level only;
- define what happens when Bunker is activated;
- define what happens when Bunker is deactivated;
- define how existing active/paused/deleted reminders behave;
- define what happens to reminders created while Bunker is active;
- define how `next_run_at` should be recalculated after exiting Bunker;
- define how worker should skip reminders during Bunker;
- define expected Telegram UX and copy;
- define localization needs for ru/kk/en;
- define data model options;
- recommend one data model direction;
- define migration implications;
- define tests needed for implementation;
- define follow-up implementation ticket split;
- update docs/DECISIONS.md with ADR if a decision is accepted;
- update docs/BACKLOG.md / docs/ROADMAP.md if needed.

### Out of scope

Do not implement:

- `/bunker` command;
- Bunker menu button behavior;
- migrations;
- database models;
- worker changes;
- reminder service changes;
- status snapshot code;
- Telegram callbacks;
- tests for runtime code;
- release tag changes.

## Design questions to answer

### Core behavior

- Is Bunker global per user?
- Does Bunker pause all reminders or only active reminders?
- Should already paused reminders remain paused after Bunker exits?
- Should deleted reminders be ignored?
- Should new reminders created during Bunker be:
  - immediately paused;
  - active but suppressed by user bunker state;
  - or rejected until Bunker exits?

### Snapshot behavior

- What exactly is stored when Bunker activates?
- Is snapshot per reminder status enough?
- Do we need `previous_status` for every reminder?
- Should snapshot be stored as JSON, separate table, or state rows?

### Exit behavior

- On Bunker deactivate, which reminders become active again?
- Which remain paused?
- How should `next_run_at` be recalculated?
- Should no-catch-up-storm helper be applied?
- What happens if active window is currently closed?

### Worker behavior

- Should worker check user-level bunker state before delivery?
- Should worker ignore reminders in Bunker without changing reminder status?
- Should Bunker create delivery records or not? Probably not.

### UX behavior

Main menu top-level future button:

```text
[Бункер 🟢/🔴]

Possible states:

Бункер выключен;
Бункер активен;
Activate Bunker;
Deactivate Bunker;
confirm activation;
confirm deactivation.

Need to decide if activation requires confirmation.

Localization

Design copy for:

Russian;
Kazakh;
English.
Recommended design direction

Executor should propose a recommended approach, but initial preference is:

Bunker is per-user;
Bunker does not rewrite every reminder status if avoidable;
Worker checks user-level bunker state and skips delivery;
A snapshot is stored only if reminders statuses need restoration;
Reminders that were paused before Bunker remain paused after exit;
Active reminders resume with recalculated next_run_at;
No catch-up storm after exit.
Deliverables

Expected docs:

docs/design/DIREM-023-bunker-mode.md or equivalent;
ADR entry in docs/DECISIONS.md if a decision is made;
optional update to docs/BACKLOG.md / docs/ROADMAP.md;
this ticket file.
README update

No README update required unless design docs introduce a parked feature note.

README must not claim Bunker Mode is implemented.

CHANGELOG update

No CHANGELOG update required unless docs policy says planning docs are tracked there.

Do not claim Bunker Mode is added.

Tests

No runtime tests required because this is design-only.

If test plan is documented, include intended future tests:

activate Bunker;
skip worker delivery;
preserve paused reminders;
restore active reminders;
recalculate next_run_at;
handle reminders created during Bunker.
Verification commands
git status
git diff

If code files change, stop and report.

Acceptance checklist
 Bunker Mode behavior is clearly defined.
 Data model direction is recommended.
 Worker behavior is defined.
 UX behavior is defined.
 Edge cases are listed.
 Follow-up implementation tickets are proposed.
 README does not claim Bunker is implemented.
 No source code was changed.
 No migration was added.
 No release tag was created.
 No local DI-CODE reference docs were staged.
Implementation guard
Design only.
Do not implement Bunker Mode.
Do not add bot commands.
Do not add callbacks.
Do not add migrations.
Do not modify worker logic.
Do not modify reminder logic.
Do not update README as if Bunker exists.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
If design reveals implementation needs, propose follow-up tickets.
Expected result summary

After this ticket:

Bunker Mode is scoped and designed;
implementation risks are known;
next implementation tickets can be cut safely.
