# DIREM-014 — Inline Reminder Control Buttons

## Status
Ready for implementation

## Version target
`DIREM v0.1.0 — Core MVP`

## Purpose

Improve Telegram UX for existing reminder control flows.

Currently `/pause`, `/resume` and `/delete` can select reminders by public number or id. This ticket adds inline buttons for selecting reminders directly in Telegram.

This is a UX polish ticket. It must not add new reminder product features.

## Context

Already implemented:

- DIREM-001 — project skeleton
- DIREM-002 — domain model / database schema
- DIREM-003 — schedule calculation domain
- DIREM-004 — user registration + `/timezone`
- DIREM-005 — `/new`
- DIREM-006 — `/list`
- DIREM-007 — `/pause` and `/resume`
- DIREM-008 — `/delete`
- DIREM-009 — worker delivery MVP
- DIREM-010 — runtime smoke / release readiness
- DIREM-011 — `/new` callback session injection fix
- DIREM-012 — control prompt active-window rendering fix
- DIREM-013 — Telegram command menu and `/cancel`

Current behavior:

- `/pause`, `/resume` and `/delete` work;
- reminder selection works by public number or id;
- `/delete` asks for confirmation;
- `/cancel` clears active FSM flows;
- worker delivery MVP works;
- retries/history/dashboard/webhook are not implemented.

## Scope

Add inline buttons for existing reminder control flows.

Need:

- add inline keyboard rendering for `/pause`;
- add inline keyboard rendering for `/resume`;
- add inline keyboard rendering for `/delete`;
- each selectable reminder should have a clear button label;
- callback data must be short and safe for Telegram callback limits;
- selecting a `/pause` reminder by button should pause it;
- selecting a `/resume` reminder by button should resume it and recalculate `next_run_at`;
- selecting a `/delete` reminder by button should enter delete confirmation;
- delete confirmation should use inline buttons:
  - confirm delete;
  - cancel;
- preserve existing manual number/id selection fallback if already implemented;
- preserve user isolation:
  - user cannot control another user's reminder by callback data;
- invalid/stale callback data should return a friendly response;
- deleted reminders must not appear in selection buttons;
- paused reminders should not appear in `/pause` selection;
- active reminders should not appear in `/resume` selection;
- `/list` should reflect changes after button actions;
- keep handlers thin;
- reuse existing `ReminderControlService` where practical;
- add tests for callback data parsing/rendering/control service behavior;
- update `/help` only if wording needs clarification;
- update README;
- update RUNTIME_SMOKE;
- update CHANGELOG.

## Out of scope

Do not implement:

- language selection;
- i18n foundation;
- new reminder features;
- reminder editing;
- delivery history command;
- retry scheduler;
- dashboard;
- webhook mode;
- Redis/Celery;
- AI features;
- web UI;
- complex pagination unless absolutely necessary;
- command menu changes unrelated to inline control.

## UX requirements

Button labels should be readable and compact.

Example button labels:

```text
1. Drink water
2. Morning check-in
3. Stretch

For delete confirmation:

Delete “Drink water”?
[Delete] [Cancel]

If a callback points to a reminder that no longer exists or no longer belongs to the user:

This reminder is no longer available.

If the reminder state changed before the click:

This reminder can no longer be changed from this action.
Acceptance criteria
/pause shows inline buttons for active reminders;
tapping a pause button pauses the selected reminder;
/resume shows inline buttons for paused reminders;
tapping a resume button resumes the selected reminder and recalculates next_run_at;
/delete shows inline buttons for selectable reminders;
tapping a delete button asks for inline confirmation;
confirming delete removes the reminder from /list;
canceling delete does not delete the reminder;
manual number/id fallback still works if it existed before;
user isolation is preserved for callbacks;
stale/invalid callbacks do not crash the bot;
/list reflects button actions;
worker delivery behavior remains unchanged;
README/RUNTIME_SMOKE/CHANGELOG are truthful;
tests pass.
Required checks
python -m pytest
python -m compileall src alembic tests
docker compose config
Optional runtime smoke

Only if real Telegram bot token is configured:

/start
/timezone
Asia/Almaty
/new
/list
/pause
tap reminder button
/list
/resume
tap reminder button
/list
/delete
tap reminder button
tap cancel
/delete
tap reminder button
tap confirm delete
/list

Expected:

inline buttons appear for /pause, /resume and /delete;
pause/resume/delete actions work through buttons;
delete confirmation works;
manual fallback does not break;
worker delivery still works for active reminders.