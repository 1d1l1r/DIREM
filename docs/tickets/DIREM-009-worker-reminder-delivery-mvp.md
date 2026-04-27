# DIREM-009 — Worker Reminder Delivery MVP

## Status
Ready for implementation

## Version target
`DIREM v0.1.0 — Core MVP`

## Purpose

Implement minimal worker-side scheduled reminder delivery for active reminder records.

After this ticket, DIREM should be able to send due reminders to Telegram users.

## Context

Already implemented:

- DIREM-001 — project skeleton
- DIREM-002 — domain model / database schema
- DIREM-003 — schedule calculation domain
- DIREM-004 — user registration + `/timezone`
- DIREM-005 — `/new` reminder creation flow
- DIREM-006 — `/list` reminder viewing flow
- DIREM-007 — `/pause` and `/resume` status flows
- DIREM-008 — `/delete` reminder deletion flow

Current behavior:

- users are persisted
- user timezone is persisted as IANA timezone
- reminders can be created, listed, paused, resumed and deleted
- `next_run_at` is stored in UTC
- worker currently only logs idle heartbeat
- delivery records schema already exists
- scheduled Telegram sending is not implemented yet

## Scope

Implement minimal worker delivery loop.

Need:

- worker polling loop for due reminders;
- find active reminders where `next_run_at <= now`;
- ignore paused reminders;
- ignore deleted reminders;
- send reminder message to the user's Telegram chat;
- use persisted user `chat_id`;
- create `reminder_deliveries` record for successful delivery;
- create failed delivery record if send fails, if existing schema supports it;
- after successful delivery, calculate and persist next `next_run_at`;
- use existing schedule functions from DIREM-003;
- use user's saved IANA timezone for next-run calculation;
- apply existing no-catch-up-storm helper if relevant;
- keep worker logic thin;
- add worker/service layer if needed;
- add repository methods for due reminder selection and next-run update;
- add tests for delivery service logic;
- README/CHANGELOG update.

## Out of scope

Do not implement:

- retry scheduler;
- exponential backoff;
- delivery dashboard;
- delivery history command;
- notification templates;
- inline buttons;
- webhook mode;
- Redis/Celery;
- AI features;
- reminder editing;
- complex locking across multiple worker replicas unless trivially needed for correctness;
- production-grade observability.

## Delivery behavior

For MVP:

- worker may poll periodically;
- one worker instance is assumed;
- delivery should be best-effort;
- successful send creates delivery record and moves `next_run_at` forward;
- failed send should not crash the worker;
- failed send should be logged;
- failed send should create failed delivery record if supported by current model;
- if failed delivery handling is ambiguous, keep behavior simple and document it.

## README nuance

After D009, README may say:

- worker sends due active reminders;
- paused reminders are not sent;
- deleted reminders are not sent;
- delivery is MVP/basic;
- retries are not implemented unless actually implemented.

README must not claim production-grade retries, dashboard, webhook mode or delivery history.

## Acceptance criteria

- worker can find due active reminders;
- worker sends due reminder message to Telegram chat_id;
- paused reminders are skipped;
- deleted reminders are skipped;
- successful delivery creates delivery record;
- successful delivery advances `next_run_at`;
- next run calculation uses user timezone and existing schedule domain logic;
- worker does not crash on Telegram send failure;
- README and CHANGELOG match current behavior;
- tests pass.

## Required checks

```bash
python -m pytest
python -m compileall src alembic tests
docker compose config