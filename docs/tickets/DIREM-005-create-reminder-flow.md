# DIREM-005 — Create Reminder Flow

## Status

Ready for implementation

## Version target

```text
DIREM v0.1.0 — Core MVP
```

## Recommended branch

```text
feature/DIREM-005-create-reminder-flow
```

## Owner / Coauthors

Use canonical credits from `docs/COAUTHORS.md` and README.

---

## 1. Purpose

Implement the first real reminder user flow in Telegram:

```text
/new → title → message text → schedule type → schedule value → optional active window → confirmation → persisted reminder
```

This ticket wires together the existing foundations:

- persisted user from `DIREM-004`;
- reminder schema from `DIREM-002`;
- schedule calculation from `DIREM-003`;
- repositories/services from previous tickets.

This ticket creates reminder records and calculates `next_run_at`.

This ticket does **not** implement listing, pause/resume/delete, or worker delivery.

---

## 2. Source of truth

Read before implementation:

```text
docs/CONCEPT.md
docs/PRODUCT_SCOPE.md
docs/ARCHITECTURE.md
docs/VERSIONING.md
docs/COAUTHORS.md
docs/ROADMAP.md
docs/DECISIONS.md
```

Follow especially:

```text
ADR-003 — Split bot service and worker service
ADR-004 — Store timestamps in UTC, interpret user schedules via IANA timezones
ADR-008 — Use docs and tickets as source of truth for implementation executor
ADR-012 — Reject overnight active windows in MVP
ADR-013 — Avoid catch-up storms after downtime
ADR-014 — Keep MVP single-user friendly but multi-user capable
```

---

## 3. Scope

### In scope

Implement:

- `/new` Telegram command;
- FSM create reminder flow;
- reminder creation service;
- repository create operation wiring if still skeleton-only;
- interval schedule creation;
- daily schedule creation;
- optional active window input;
- validation of title/message/schedule/window;
- `next_run_at` calculation using `DIREM-003` schedule functions;
- confirmation screen before saving;
- cancellation if simple and clean;
- README/CHANGELOG update;
- tests for reminder creation service and flow helpers where practical.

### Out of scope

Do **not** implement:

- `/list`;
- `/pause`;
- `/resume`;
- `/delete`;
- worker due reminder delivery;
- Telegram sending of scheduled reminders;
- delivery log creation from worker;
- advanced edit flow;
- multiple active windows;
- overnight active windows;
- templates/rituals;
- dashboard;
- Redis/Celery;
- webhook mode;
- AI generation.

---

## 4. User flow

### 4.1. Start creation

User sends:

```text
/new
```

Bot ensures user exists. If user has no timezone, use `UTC` and suggest `/timezone`.

Bot asks for reminder title.

Example:

```text
Create reminder.

Send a short title.
Example: Morning focus
```

### 4.2. Title input

User sends title.

Rules:

- required;
- trim whitespace;
- reasonable max length, e.g. 80 chars;
- reject empty title.

Bot asks for message text.

### 4.3. Message text input

User sends message text.

Rules:

- required;
- trim whitespace;
- reasonable max length, e.g. 1000 chars;
- reject empty text.

Bot asks for schedule type with inline buttons.

Options:

```text
Interval
Daily time
```

### 4.4. Interval schedule

If user chooses interval, ask for minutes.

Rules:

- positive integer;
- recommended minimum: 1;
- recommended maximum: 1440;
- reject invalid input.

Example:

```text
Send interval in minutes.
Example: 45
```

### 4.5. Daily schedule

If user chooses daily, ask for local time.

Format:

```text
HH:MM
```

Examples:

```text
09:00
22:30
```

Rules:

- valid 24-hour time;
- interpreted in user's timezone;
- rejects invalid input.

### 4.6. Active window

After schedule value, ask whether to add active window.

Options:

```text
No active window
Set active window
```

If no active window:

- reminder is active all day.

If set active window, ask for:

```text
HH:MM-HH:MM
```

Example:

```text
10:00-18:00
```

Rules:

- both times required;
- `active_from < active_to`;
- overnight windows rejected;
- use `DIREM-003` active window validation;
- for daily schedule, daily time must be inside active window.

### 4.7. Confirmation

Before saving, bot shows summary:

```text
Create reminder?

Title: Morning focus
Message: Вернись к текущему шагу.
Schedule: every 45 minutes
Timezone: Asia/Almaty
Active window: 10:00-18:00
First run: 2026-04-26 15:45 Asia/Almaty
```

Buttons:

```text
Create
Cancel
```

On confirm:

- create reminder;
- set status `active`;
- calculate and persist `next_run_at` in UTC;
- clear FSM state;
- respond with success.

Example:

```text
Reminder created.
First run: 2026-04-26 15:45 Asia/Almaty
```

---

## 5. Technical requirements

### 5.1. Reminder service

Create or extend:

```text
src/direm/services/reminder_service.py
```

Required behavior:

- validate create request;
- use user's timezone;
- call schedule domain functions;
- create reminder through repository;
- return created reminder and first run display data.

Handlers should not calculate `next_run_at` directly.

### 5.2. Repository wiring

Use existing reminder repository skeleton from `DIREM-002`.

Implement only what is needed:

- create reminder;
- get by id if needed for confirmation result;
- no list/pause/resume/delete behavior unless already present and trivial.

### 5.3. FSM state

Add create reminder FSM states.

Suggested states:

```text
waiting_title
waiting_message_text
waiting_schedule_type
waiting_interval_minutes
waiting_daily_time
waiting_active_window_choice
waiting_active_window_value
waiting_confirmation
```

Use aiogram FSM or the existing project pattern from `/timezone`.

Do not create a parallel state system if one already exists.

### 5.4. Parsing helpers

Add small parsing helpers if useful:

- parse HH:MM time;
- parse HH:MM-HH:MM active window;
- parse interval minutes.

Keep parsing helpers separate from Telegram text where practical.

Suggested location:

```text
src/direm/domain/parsing.py
```

or inside reminder service if small.

### 5.5. Formatting helpers

Add small user-facing formatting helper for summary/first run if useful.

Keep it simple.

Do not add full localization framework.

---

## 6. Validation rules

### Title

- non-empty after trim;
- max length 80 chars.

### Message text

- non-empty after trim;
- max length 1000 chars.

### Interval minutes

- integer;
- `1 <= interval_minutes <= 1440`.

### Daily time

- format `HH:MM`;
- valid 24-hour local time.

### Active window

- empty/all-day allowed;
- format `HH:MM-HH:MM` if set;
- same-day only;
- `active_from < active_to`;
- daily_time must be inside active window when schedule type is daily.

---

## 7. Bot command list

After this ticket, README should list as available:

```text
/start
/help
/timezone
/new
/version
/credits
```

Still not implemented:

```text
/list
/pause
/resume
/delete
real worker delivery logic
```

---

## 8. README update

Update README to state:

```text
Users can now create reminder records with /new. Reminder delivery is still not implemented; the worker does not send scheduled reminders yet.
```

Also update smoke test to include:

```text
/start
/timezone
Asia/Almaty
/new
```

Do not claim that scheduled messages are sent yet.

---

## 9. CHANGELOG update

Update `CHANGELOG.md` under `[0.1.0] - Unreleased`.

Suggested entry:

```markdown
### Added
- Added `/new` reminder creation flow for interval and daily reminders.
- Added reminder creation service wiring with timezone-aware `next_run_at` calculation.
```

---

## 10. Tests

Add tests where practical.

Recommended tests:

### parsing tests

- parse valid `HH:MM`;
- reject invalid `25:00`;
- parse valid `10:00-18:00`;
- reject overnight `18:00-10:00`.

### service tests

- create interval reminder uses user timezone;
- create interval reminder sets status active;
- create interval reminder calculates future `next_run_at`;
- create daily reminder calculates future `next_run_at`;
- daily reminder outside active window rejects;
- invalid title/message rejects.

### command/handler tests

Only if current testing setup makes this simple. Do not build a large Telegram integration harness in this ticket.

---

## 11. Acceptance checklist

This ticket is complete when:

- `/new` command exists;
- user can enter title;
- user can enter message text;
- user can choose interval schedule;
- user can choose daily schedule;
- user can choose no active window;
- user can set valid active window;
- invalid active window is rejected;
- overnight active window is rejected;
- confirmation screen appears before saving;
- confirmed reminder is persisted;
- persisted reminder has `status = active`;
- persisted reminder has `next_run_at` in UTC;
- schedule functions from `DIREM-003` are reused;
- handlers remain thin and call services;
- README says `/new` is available but delivery is not;
- CHANGELOG includes `/new` creation flow;
- `python -m pytest` passes;
- `python -m compileall src alembic tests` passes;
- `docker compose config` passes;
- no `/list`, `/pause`, `/resume`, `/delete` implementation is added;
- worker still does not send reminders.

---

## 12. Suggested verification commands

```bash
python -m pytest
python -m compileall src alembic tests
docker compose config
```

Optional manual smoke test:

```text
/start
/timezone
Asia/Almaty
/new
```

Create:

```text
Title: Morning focus
Message: Вернись к текущему шагу.
Schedule: interval 45
Active window: 10:00-18:00
Confirm: Create
```

Expected:

- bot confirms reminder creation;
- no scheduled Telegram message is sent by worker yet.

---

## 13. Implementation guard

For Bushid Ronin V:

```text
Implement only DIREM-005 /new reminder creation flow.
Do not implement list/pause/resume/delete.
Do not implement worker due reminder delivery.
Use existing schedule domain functions for next_run_at.
Use existing user timezone from DIREM-004.
Keep handlers thin and move business logic to services.
Do not add new infrastructure or out-of-scope dependencies.
Do not claim delivery works in README.
```

---

## 14. Expected result summary

After this ticket:

```text
Users can create reminder records through Telegram /new.
Reminders have schedule config and next_run_at.
The bot still cannot list/manage reminders.
The worker still does not send scheduled reminders.
Management and delivery come in later tickets.
```

