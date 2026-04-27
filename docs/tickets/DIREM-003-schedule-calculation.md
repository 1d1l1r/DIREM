# DIREM-003 — Schedule Calculation Domain

## Status

Ready for implementation

## Version target

```text
DIREM v0.1.0 — Core MVP
```

## Recommended branch

```text
feature/DIREM-003-schedule-calculation
```

## Owner / Coauthors

Use canonical credits from `docs/COAUTHORS.md` and README.

---

## 1. Purpose

Implement the pure domain logic for calculating reminder schedules.

This ticket adds deterministic, testable schedule functions for:

- interval reminders;
- daily fixed-time reminders;
- active window validation;
- active window checks;
- no catch-up storm behavior;
- timezone-aware local schedule interpretation;
- UTC persistence boundaries.

This ticket does **not** implement Telegram reminder creation flows or real worker delivery.

The goal is to make schedule calculation reliable before wiring it into `/new`, repositories or the worker.

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
ADR-004 — Store timestamps in UTC, interpret user schedules via IANA timezones
ADR-012 — Reject overnight active windows in MVP
ADR-013 — Avoid catch-up storms after downtime
```

---

## 3. Scope

### In scope

Implement pure schedule calculation domain module:

- schedule input/value objects if useful;
- timezone validation helper;
- active window validation;
- local-time active window check;
- next run calculation for interval reminders;
- next run calculation for daily reminders;
- helper to move a due reminder to the next valid future time;
- unit tests for all schedule edge cases;
- README/CHANGELOG update noting schedule domain logic exists but is not wired to UX/worker yet.

### Out of scope

Do **not** implement:

- Telegram `/new` flow;
- Telegram `/list`, `/pause`, `/resume`, `/delete`;
- `/timezone` command flow;
- repository write operations beyond what already exists;
- worker due reminder query/claim/send loop;
- Telegram delivery;
- retries;
- reminder creation UX;
- dashboard;
- Redis/Celery;
- webhook mode;
- AI generation.

---

## 4. Recommended module structure

Suggested location:

```text
src/direm/domain/schedules.py
```

Optional supporting tests:

```text
tests/unit/test_schedules.py
```

Keep the module independent from:

- Telegram;
- aiogram;
- SQLAlchemy sessions;
- repositories;
- worker loops.

Domain functions should be pure or near-pure and easy to unit test.

---

## 5. Required behavior

### 5.1. Timezone validation

Implement helper:

```python
validate_timezone(timezone: str) -> str
```

or equivalent.

Rules:

- accepts valid IANA timezone strings, e.g. `Asia/Almaty`, `UTC`;
- rejects invalid strings with a domain-level exception or clear validation result;
- does not silently fallback to UTC for invalid user input.

Preferred implementation: Python standard library `zoneinfo`.

### 5.2. Active window validation

MVP supports only same-day windows:

```text
active_from < active_to
```

Rules:

- if both `active_from` and `active_to` are `None`, reminder is active all day;
- if one is set and the other is missing, reject as invalid;
- if `active_from >= active_to`, reject as unsupported in MVP;
- overnight windows are not supported in MVP.

### 5.3. Active window check

Implement helper similar to:

```python
is_inside_active_window(
    dt_utc: datetime,
    timezone: str,
    active_from: time | None,
    active_to: time | None,
) -> bool
```

Rules:

- `dt_utc` is timezone-aware UTC;
- convert `dt_utc` to local time using `timezone`;
- compare local time against active window;
- all-day reminder returns `True`;
- same-day window is inclusive at start and exclusive at end:

```text
active_from <= local_time < active_to
```

### 5.4. Interval next run calculation

Implement helper similar to:

```python
compute_next_interval_run(
    now_utc: datetime,
    interval_minutes: int,
    timezone: str,
    active_from: time | None = None,
    active_to: time | None = None,
) -> datetime
```

Rules:

- `now_utc` must be timezone-aware UTC;
- `interval_minutes` must be positive;
- base next run is `now_utc + interval_minutes`;
- if no active window, return base next run;
- if base next run falls inside active window, return it;
- if base next run is before today's active window, return today's active_from in UTC;
- if base next run is at/after today's active_to, return next day's active_from in UTC;
- overnight active windows are rejected by validation.

### 5.5. Daily next run calculation

Implement helper similar to:

```python
compute_next_daily_run(
    now_utc: datetime,
    daily_time: time,
    timezone: str,
    active_from: time | None = None,
    active_to: time | None = None,
) -> datetime
```

Rules:

- `now_utc` must be timezone-aware UTC;
- interpret `daily_time` in user's timezone;
- if today's local daily_time is still in the future, return today at daily_time converted to UTC;
- if today's local daily_time has passed, return tomorrow at daily_time converted to UTC;
- if active window is set, daily_time must fall inside active window;
- if daily_time is outside active window, reject as invalid config rather than silently moving it.

### 5.6. No catch-up storm helper

Implement helper that can be used later by worker:

```python
compute_next_after_due(
    now_utc: datetime,
    schedule_type: str,
    interval_minutes: int | None,
    daily_time: time | None,
    timezone: str,
    active_from: time | None = None,
    active_to: time | None = None,
) -> datetime
```

Rules:

- for interval reminders, use `now_utc + interval_minutes`, adjusted to next valid active window;
- do not attempt to replay missed runs;
- for daily reminders, compute next daily local time after `now_utc`;
- return a future UTC datetime.

---

## 6. Error handling

Create simple domain exceptions or validation result types.

Suggested exceptions:

```python
ScheduleValidationError
InvalidTimezoneError
InvalidActiveWindowError
InvalidScheduleConfigError
```

Keep them in the domain layer, for example:

```text
src/direm/domain/errors.py
```

or inside `schedules.py` if simpler.

Do not return user-facing Telegram text from domain functions.

Telegram-friendly error messages will be mapped later in bot flow tickets.

---

## 7. Tests required

Add strong unit tests for schedule calculation.

Required test cases:

### Timezone validation

- accepts `UTC`;
- accepts `Asia/Almaty`;
- rejects invalid timezone string.

### Active window validation

- accepts no active window;
- accepts `10:00–18:00`;
- rejects only `active_from` set;
- rejects only `active_to` set;
- rejects `18:00–10:00`;
- rejects `10:00–10:00`.

### Active window check

- all-day returns true;
- local time inside window returns true;
- local time before window returns false;
- local time at active_to returns false.

### Interval schedule

- no active window returns `now + interval`;
- base next run inside active window returns base;
- base next run before window returns today's active_from;
- base next run after window returns next day's active_from;
- invalid interval `0` or negative rejects.

### Daily schedule

- today future time returns today;
- today past time returns tomorrow;
- `Asia/Almaty` conversion works;
- daily_time inside active window passes;
- daily_time outside active window rejects.

### No catch-up storm

- interval reminder due after downtime returns `now + interval`, not a sequence of missed runs;
- returned time is in the future.

---

## 8. README update

Update README minimally:

- mention that schedule calculation domain functions exist;
- clearly state that Telegram reminder creation and worker delivery are still not implemented;
- do not claim user can create reminders yet.

Suggested wording:

```text
DIREM now contains tested schedule calculation domain logic. It is not yet wired into Telegram reminder creation or worker delivery.
```

---

## 9. CHANGELOG update

Update `CHANGELOG.md` under `[0.1.0] - Unreleased`.

Suggested entry:

```markdown
### Added
- Added timezone-aware schedule calculation domain logic for interval and daily reminders.
- Added active window validation and no catch-up storm scheduling behavior.
```

---

## 10. Acceptance checklist

This ticket is complete when:

- schedule domain module exists;
- timezone validation exists;
- active window validation exists;
- active window check exists;
- interval next-run calculation exists;
- daily next-run calculation exists;
- no catch-up storm helper exists;
- domain-level schedule errors exist;
- unit tests cover required cases;
- `python -m pytest` passes;
- `python -m compileall src alembic tests` passes;
- `docker compose config` passes;
- README accurately states schedule logic exists but is not wired;
- CHANGELOG includes schedule domain additions;
- no Telegram reminder flows are added;
- no worker delivery logic is added;
- no out-of-scope dependencies are added.

---

## 11. Suggested verification commands

```bash
python -m pytest
python -m compileall src alembic tests
docker compose config
```

---

## 12. Implementation guard

For Bushid Ronin V:

```text
Implement only DIREM-003 schedule calculation domain logic.
Do not implement Telegram reminder creation.
Do not implement worker due reminder delivery.
Do not wire schedule functions into bot handlers yet.
Do not add external scheduler libraries.
Use UTC-aware datetimes internally and IANA timezone strings at boundaries.
Reject overnight active windows in MVP.
Avoid catch-up storm behavior.
Keep functions pure, small and heavily unit-tested.
```

---

## 13. Expected result summary

After this ticket:

```text
DIREM can calculate valid next_run_at values in pure domain tests.
The database schema already exists from DIREM-002.
The Telegram bot still exposes only shell commands.
The worker is still a stub.
Wiring comes later.
```

