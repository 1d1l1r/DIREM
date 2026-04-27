# DIREM-008 — Delete Reminder Flow

## Status
Ready for implementation

## Version target
`DIREM v0.1.0 — Core MVP`

## Purpose

Implement `/delete` command for deleting current user's reminder records before worker delivery is introduced.

## Context

Already implemented:

- DIREM-001 — project skeleton
- DIREM-002 — domain model / database schema
- DIREM-003 — schedule calculation domain
- DIREM-004 — user registration + `/timezone`
- DIREM-005 — `/new` reminder creation flow
- DIREM-006 — `/list` reminder viewing flow
- DIREM-007 — `/pause` and `/resume` status flows

Current behavior:

- `/start` creates or updates Telegram user record
- `/timezone` persists valid IANA timezone
- `/new` creates reminder records
- `/list` shows current user's reminders
- `/pause` marks reminder as paused
- `/resume` marks reminder as active and recalculates `next_run_at`
- worker delivery is still not implemented

## Scope

Implement only `/delete` reminder flow.

Need:

- `/delete` command handler;
- show selectable reminders for current Telegram user;
- allow selecting reminder by public number or id;
- ask for confirmation before deleting;
- delete only reminders belonging to current Telegram user;
- reject invalid reminder id/number cleanly;
- reject attempts to delete another user's reminder;
- friendly empty state if user has no reminders;
- after delete, `/list` should no longer show deleted reminder;
- keep handlers thin;
- add service/repository methods as needed;
- tests;
- README/CHANGELOG update.

## Out of scope

Do not implement:

- reminder editing;
- soft delete unless existing architecture clearly requires it;
- undo restore;
- inline buttons unless already trivial;
- worker due reminder delivery;
- scheduled Telegram sending;
- retries;
- delivery history;
- dashboard/webhook/AI/Redis/Celery.

## README nuance

After D008, README may say:

- `/delete` deletes current user's reminder records;
- `/new`, `/list`, `/pause`, `/resume`, `/delete` are available;
- worker delivery still does not send scheduled reminders.

README must not claim that reminder delivery works.

## Acceptance criteria

- `/delete` works after `/start`;
- new user with no reminders gets empty-state message;
- user can delete own reminder by public number or id;
- user cannot delete another user's reminder;
- invalid selection is rejected cleanly;
- confirmation is required before deletion;
- `/list` no longer shows deleted reminder;
- worker delivery remains unimplemented;
- README and CHANGELOG match current behavior;
- tests pass.

## Required checks

```bash
python -m pytest
python -m compileall src alembic tests
docker compose config