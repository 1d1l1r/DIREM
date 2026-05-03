# DIREM-025 — Worker Suppression for Bunker Mode

## Status
Ready for implementation

## Version target
`DIREM v0.2.0 — Bunker Mode`

## Workstream
Backend / Worker

## Recommended branch
`feature/DIREM-025-bunker-worker-suppression`

## Owner / Contributors

Project Owner:
- 1D1L1R

Contributors for this ticket:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — implementation executor

## Purpose

Make the worker respect user-level Bunker state.

DIREM-024 added persisted Bunker state foundation:

- `users.bunker_active`
- `users.bunker_activated_at`
- `BunkerService`
- repository methods

DIREM-025 wires this state into worker delivery behavior.

When a user has Bunker active, due reminders for that user must not be delivered.

This ticket must not add Telegram UI, `/bunker`, menu buttons or Bunker deactivation recalculation.

## Source of truth

Read before implementation:

- docs/CONCEPT.md
- docs/ARCHITECTURE.md
- docs/DECISIONS.md
- docs/design/DIREM-023-bunker-mode.md
- docs/BACKLOG.md
- docs/ROADMAP.md
- docs/tickets/DIREM-025-bunker-worker-suppression.md

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

- DIREM-023 — Bunker Mode Design
- DIREM-024 — Bunker State Foundation

Current behavior:

- worker selects due active reminders;
- worker sends due reminders to persisted user chat;
- worker writes `reminder_deliveries` for sent/failed attempts;
- worker advances `next_run_at` after successful delivery;
- paused/deleted reminders are skipped;
- user-level Bunker state exists but is not used by worker yet.

Accepted design:

- Bunker is user-level delivery suppression;
- Bunker does not rewrite reminder statuses;
- worker should skip users with active Bunker;
- no delivery record should be created for suppressed reminders;
- no catch-up storm after Bunker exit should be handled in a later ticket.

## Scope

### In scope

Add worker suppression for users with active Bunker.

Need:

- update due reminder selection or delivery service so reminders for users with `bunker_active = true` are not sent;
- prefer filtering bunker-active users before sending, if clean;
- add defensive guard in delivery service if practical;
- do not create `reminder_deliveries` records for bunker-suppressed reminders;
- do not mark suppressed delivery as failed;
- do not mutate reminder status;
- do not advance `next_run_at` while Bunker is active;
- keep paused/deleted reminder behavior unchanged;
- keep failed send behavior unchanged;
- add tests;
- update CHANGELOG;
- README update only if needed and must not claim user-facing Bunker exists.

### Out of scope

Do not implement:

- `/bunker` command;
- menu button;
- Telegram callbacks;
- Bunker activation/deactivation UI;
- Bunker status in `/list`;
- deactivation behavior;
- `next_run_at` recalculation after Bunker exit;
- timed Bunker;
- per-reminder snooze;
- delivery history command;
- retry scheduler;
- reminder editing;
- dashboard/webhook;
- AI features;
- web UI;
- migrations unless absolutely required.

Future tickets:

- D026 — Telegram Bunker UX / Menu Integration;
- D027 — Bunker Exit Recalculation / Runtime Polish, if needed.

## Technical requirements

- Keep worker behavior small and testable.
- Prefer query-level exclusion of bunker-active users if it fits current repository structure.
- If query-level exclusion is awkward, use delivery-service guard and ensure no send attempt occurs.
- Do not record suppressed reminders as sent or failed.
- Do not add a new delivery status unless clearly justified in the plan.
- Do not change reminder status values.
- Do not change Bunker persistence model from D024.
- Do not add migration.

## Expected behavior

Given:

- User A has `bunker_active = false`;
- User B has `bunker_active = true`;
- both have due active reminders.

Worker should:

- deliver User A reminders normally;
- not deliver User B reminders;
- not create delivery records for User B suppressed reminders;
- not advance User B reminder `next_run_at`;
- not mutate User B reminder status;
- not crash or spam scary logs.

## README update

README update is optional.

README may say only if needed:

- worker internally respects user-level Bunker suppression foundation.

README must not claim:

- Bunker Mode is available in Telegram UI;
- `/bunker` exists;
- users can toggle Bunker;
- Bunker exit recalculation is implemented.

## CHANGELOG update

Add under `[Unreleased]`:

```text
- Added worker-side suppression for reminders owned by users with active Bunker state.

Do not say Bunker Mode is user-facing yet.

Tests

Required tests:

due active reminder for non-Bunker user is still delivered;
due active reminder for Bunker-active user is not sent;
no delivery record is created for Bunker-suppressed reminder;
suppressed reminder next_run_at is not advanced;
suppressed reminder status is not changed;
paused/deleted reminders still behave as before;
failed send behavior for non-Bunker user still works;
repository/delivery query handles mixed Bunker and non-Bunker users.
Manual smoke

No user-facing smoke yet because Bunker UI does not exist.

Optional internal/dev smoke if convenient:

Activate Bunker state in DB/service for a test user.
Create due reminder for that user.
Run worker.
Verify no Telegram message is sent.
Verify no delivery record is created.
Verify reminder remains active and due.
Acceptance checklist
 Worker suppresses reminders for Bunker-active users.
 Suppressed reminders are not sent.
 Suppressed reminders do not create delivery records.
 Suppressed reminders do not advance next_run_at.
 Reminder statuses are not mutated.
 Non-Bunker delivery behavior still works.
 Failed send behavior still works.
 No Telegram UI was added.
 No migration was added.
 CHANGELOG is truthful.
 Tests pass.
 No local DI-CODE reference docs were staged.
 No release tag was created.
Verification commands
python -m pytest
python -m compileall src alembic tests
docker compose config
git status
git diff
Git / GitHub expectations
Follow DI-CODE_GITHUB_WORKFLOW.md.
Use feature/DIREM-025-bunker-worker-suppression.
Do not commit directly to main.
Do not create a release tag.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
Report branch, commit, changed files, checks and push state.
Implementation guard
Implement only Bunker worker suppression.
Do not implement Telegram Bunker UI.
Do not implement /bunker command.
Do not implement menu button.
Do not mutate reminder statuses.
Do not advance next_run_at for suppressed reminders.
Do not create delivery records for suppressed reminders.
Do not implement Bunker exit recalculation.
Do not implement timed Bunker.
Do not implement delivery history/retries/editing.
Do not add dashboard/webhook/AI/web UI.
Do not add migrations unless implementation cannot meet acceptance without one; if so, stop and report first.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
If suppression design conflicts with D023/D024, stop and report.
Expected result summary

After this ticket:

worker respects user-level Bunker state;
Bunker-active users are not sent reminders;
reminder statuses remain untouched;
Telegram Bunker UI remains a separate future ticket.