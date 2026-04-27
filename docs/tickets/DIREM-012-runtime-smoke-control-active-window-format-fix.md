# DIREM-012 — Runtime Smoke: Fix Reminder Control Active Window Formatting

## Status
Ready for implementation

## Version target
`DIREM v0.1.0 — Core MVP`

## Purpose

Fix runtime smoke blocker for `/pause`, `/resume` and `/delete`.

The commands are routed correctly, but crash while rendering selectable reminder prompts because `_format_active_window` is called with wrong arguments.

This is a bugfix-only ticket.

## Runtime evidence

During real Telegram runtime smoke:

- `/new` works;
- worker delivery works;
- `/pause`, `/resume` and `/delete` do not complete;
- bot logs show:

```text
TypeError: _format_active_window() missing 1 required positional argument: 'active_to'

Observed paths:

src/direm/bot/handlers/delete.py
→ ReminderControlService.render_selection_prompt
→ _format_active_window(reminder)
src/direm/bot/handlers/pause_resume.py
→ ReminderControlService.render_selection_prompt
→ _format_active_window(reminder)
Scope

Need:

inspect src/direm/services/reminder_control_service.py;
fix _format_active_window usage/signature mismatch;
ensure active window formatting works for:
no active window;
active_from + active_to;
reminders created through real /new;
ensure /pause renders selectable reminders;
ensure /resume renders selectable reminders;
ensure /delete renders selectable reminders;
add regression tests for render_selection_prompt;
add handler/service tests for pause/resume/delete prompt rendering if existing test style allows;
update CHANGELOG;
README/RUNTIME_SMOKE update only if needed.
Out of scope

Do not implement:

new product features;
command menu setup;
inline buttons;
retry scheduler;
delivery history command;
dashboard/webhook/Redis/Celery/AI;
reminder editing;
large refactor.
Acceptance criteria
/pause no longer crashes at selection prompt;
/resume no longer crashes at selection prompt;
/delete no longer crashes at selection prompt;
selectable reminder prompts show active window correctly or show that there is no active window;
active reminder can be paused;
paused reminder can be resumed;
reminder can be deleted;
/list reflects pause/resume/delete state;
automated tests pass;
CHANGELOG mentions runtime smoke fix.
Required checks
python -m pytest
python -m compileall src alembic tests
docker compose config
Optional owner runtime smoke
/start
/timezone
Asia/Almaty
/new
/list
/pause
/list
/resume
/list
/delete
/list

Expected:

/pause, /resume, /delete respond with selection prompts;
no _format_active_window traceback appears;
worker can be restarted after control commands are verified.