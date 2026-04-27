# DIREM-007 — Pause / Resume Reminder Flow

## Goal

Implement `/pause` and `/resume` commands for existing reminder records.

## Scope

Need:

- `/pause` command;
- `/resume` command;
- show user's reminders before choosing target;
- allow selecting reminder by id/public number;
- only current Telegram user's reminders can be paused/resumed;
- paused reminder gets `status = paused`;
- resumed reminder gets `status = active`;
- on resume, recalculate `next_run_at` using user's timezone and schedule functions from DIREM-003;
- reject pause/resume for reminders owned by another user;
- reject invalid reminder id/number;
- friendly empty state if user has no reminders;
- keep handlers thin;
- add service layer if needed;
- add repository methods for status update;
- tests;
- README/CHANGELOG update.

## Out of scope

Do not implement:

- `/delete`;
- editing reminders;
- worker delivery;
- scheduled Telegram sending;
- retries;
- inline buttons unless already trivial;
- dashboard/webhook/AI/Redis/Celery.

## Acceptance criteria

- `/pause` pauses current user's active reminder;
- `/resume` resumes current user's paused reminder;
- resumed reminder gets fresh `next_run_at`;
- reminders from other users cannot be paused/resumed;
- invalid ids are rejected cleanly;
- `/list` reflects changed statuses;
- worker delivery remains unimplemented;
- README and CHANGELOG are truthful;
- tests pass.

## Required checks

```bash
python -m pytest
python -m compileall src alembic tests
docker compose config