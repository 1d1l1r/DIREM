# DIREM-006 — List Reminders Flow

Status: Ready for implementation  
Target version: 0.1.0  
Executor: Bushid Ronin V  
Reviewer: Rein Hard V  

## Goal

Implement `/list` command for viewing the current user's reminder records in Telegram.

## Context

Already implemented:

- DIREM-001 — project skeleton
- DIREM-002 — domain model / database schema
- DIREM-003 — schedule calculation domain
- DIREM-004 — user registration + `/timezone` flow
- DIREM-005 — `/new` reminder creation flow

Current behavior:

- `/start` creates or updates Telegram user record
- existing timezone is preserved
- new users default to UTC
- `/timezone` persists valid IANA timezone
- `/new` creates interval or daily reminder records
- `next_run_at` is calculated and stored in UTC
- worker delivery is still not implemented

## Scope

Implement only `/list` reminders flow.

Need:

- `/list` command handler;
- list reminders only for current Telegram user;
- use existing user lookup from DIREM-004;
- add reminder repository read method, e.g. `list_by_user_id`;
- add service layer if needed, e.g. `ReminderListService`;
- show active reminders first;
- show reminder fields:
  - title;
  - schedule type;
  - schedule value;
  - optional active window;
  - `next_run_at`;
  - status;
- convert `next_run_at` from UTC to user's saved IANA timezone;
- show friendly empty state if user has no reminders;
- keep handlers thin;
- tests;
- README/CHANGELOG update.

## Out of scope

Do not implement:

- `/pause`;
- `/resume`;
- `/delete`;
- reminder editing;
- inline buttons;
- pagination unless trivially needed;
- worker due reminder delivery;
- scheduled Telegram sending;
- retries;
- dashboard/webhook/AI/Redis/Celery.

## README nuance

After D006, README may say:

- `/list` shows current user's reminder records;
- `/new` creates reminder records;
- worker delivery still does not send scheduled reminders.

README must not claim that reminder delivery works.

Also clean stale wording if README still describes `/new` as not implemented.

## Acceptance criteria

- `/list` works after `/start`;
- new user with no reminders gets empty-state message;
- user with reminders sees reminders created through `/new`;
- `next_run_at` is displayed in user's saved timezone;
- reminders from other Telegram users are not shown;
- delivery remains unimplemented;
- README and CHANGELOG match current behavior;
- tests pass.

## Required checks

```bash
python -m pytest
python -m compileall src alembic tests
docker compose config