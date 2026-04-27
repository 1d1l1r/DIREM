# DIREM-004 — User Registration & Timezone Flow

## Status

Ready for implementation

## Version target

```text
DIREM v0.1.0 — Core MVP
```

## Recommended branch

```text
feature/DIREM-004-user-timezone-flow
```

## Owner / Coauthors

Use canonical credits from `docs/COAUTHORS.md` and README.

---

## 1. Purpose

Wire the first real user-facing persisted behavior into the Telegram bot:

- create/update user record on `/start`;
- allow the user to view and set their IANA timezone via `/timezone`;
- validate timezone using the pure domain logic from `DIREM-003`;
- persist timezone in the `users` table;
- update `/help` and `/status` minimally if needed.

This ticket prepares the bot for reminder creation in later tickets.

This ticket does **not** implement reminder creation, reminder listing, pause/resume/delete, or worker delivery.

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
ADR-014 — Keep MVP single-user friendly but multi-user capable
```

---

## 3. Scope

### In scope

Implement:

- user service for Telegram user registration/update;
- `/start` creates or updates user record;
- `/timezone` command;
- timezone input flow;
- timezone validation via domain schedule/timezone helper;
- persistence of `users.timezone`;
- current timezone display;
- minimal `/status` update to show timezone if not already present;
- tests for user service/timezone flow helpers where practical;
- README and CHANGELOG updates.

### Out of scope

Do **not** implement:

- `/new`;
- `/list`;
- `/pause`;
- `/resume`;
- `/delete`;
- reminder creation flow;
- schedule wiring into reminders;
- worker due reminder logic;
- Telegram delivery;
- active reminder status screen;
- admin commands;
- dashboard;
- Redis/Celery;
- webhook mode;
- AI generation.

---

## 4. User behavior

### 4.1. `/start`

When a Telegram user sends `/start`, the bot should:

1. create user record if missing;
2. update basic Telegram profile fields if user already exists;
3. preserve existing timezone if already set;
4. set default timezone to `UTC` for new users;
5. respond with short introduction and suggest `/timezone`.

Expected message style:

```text
DIREM is active.

I can help you keep regular returns to intention.
Current timezone: UTC

Set your local timezone with /timezone, for example: Asia/Almaty
```

Exact wording may differ, but keep it concise.

### 4.2. `/timezone`

When user sends `/timezone`, the bot should show:

- current timezone;
- short instruction;
- examples.

Example:

```text
Current timezone: UTC

Send your timezone as an IANA name, for example:
Asia/Almaty
Europe/Moscow
UTC
```

Then bot should wait for the next text message from the same user as timezone input.

### 4.3. Valid timezone input

If user sends a valid timezone, for example:

```text
Asia/Almaty
```

Bot should:

- validate it;
- save it to `users.timezone`;
- clear timezone flow state;
- confirm the new timezone.

Example:

```text
Timezone updated: Asia/Almaty
```

### 4.4. Invalid timezone input

If user sends invalid timezone:

```text
Almaty
```

Bot should:

- not save it;
- keep the flow active;
- return a short error with examples.

Example:

```text
Invalid timezone.
Use an IANA name, for example: Asia/Almaty or UTC.
```

Do not silently fallback to UTC.

### 4.5. Cancel behavior

If simple cancellation support already exists, allow cancel.

If not, implement a small `/cancel` only for active timezone flow if it is cheap and clean.

If adding `/cancel` risks scope creep, skip it and keep the flow simple.

---

## 5. Technical requirements

### 5.1. User service

Add or extend:

```text
src/direm/services/user_service.py
```

Required behavior:

- get user by Telegram user id;
- create user from Telegram message metadata;
- update existing user's chat_id/username/first_name;
- get-or-create user;
- update timezone.

Keep service logic separate from handlers.

Handlers should not perform direct SQLAlchemy queries.

### 5.2. Repositories

Use existing repository skeletons from `DIREM-002`.

If repository functions are stubs, implement only what is needed:

- get by Telegram user id;
- create;
- update profile fields;
- update timezone.

Do not implement unrelated repository operations.

### 5.3. FSM / user state

Use aiogram FSM or existing `user_states` repository, whichever is already consistent with the project skeleton.

MVP acceptable options:

1. aiogram FSM for `/timezone` flow;
2. DB-backed `user_states` if already simple;
3. in-memory FSM only if current architecture uses it and README notes restart limitation.

Preferred:

- keep it simple;
- do not overbuild persistence if it requires large changes;
- do not mix business rules into FSM handlers.

### 5.4. Timezone validation

Use schedule domain helper from `DIREM-003`.

Do not duplicate timezone validation logic inside handler.

Invalid timezone should map domain error to short user-facing Telegram text.

### 5.5. `/status`

If `/status` command does not exist yet, do not create a full status screen in this ticket unless trivial.

If it already exists or can be added simply, show at least:

```text
Timezone: Asia/Almaty
Version: 0.1.0
```

Reminder counts are not required yet.

---

## 6. README update

Update README to show `/timezone` as available.

Important wording:

```text
Available now:
- /start
- /help
- /timezone
- /version
- /credits
```

Keep reminder commands in “not implemented yet”.

Mention:

```text
Users can now persist an IANA timezone. Reminder creation and delivery are still not implemented.
```

---

## 7. CHANGELOG update

Update `CHANGELOG.md` under `[0.1.0] - Unreleased`.

Suggested entry:

```markdown
### Added
- Added user registration/update on `/start`.
- Added `/timezone` flow with IANA timezone validation and persistence.
```

---

## 8. Tests

Add tests where practical.

Recommended tests:

- user service creates user with default `UTC` timezone;
- user service preserves existing timezone on repeated `/start`;
- user service updates Telegram profile fields;
- update timezone accepts `Asia/Almaty`;
- update timezone rejects invalid timezone;
- `/credits` and `/version` tests remain passing.

If DB integration testing is not set up, test pure helper/service behavior with lightweight test doubles rather than building a large test framework in this ticket.

Do not weaken existing tests.

---

## 9. Acceptance checklist

This ticket is complete when:

- `/start` creates user if missing;
- repeated `/start` does not duplicate user;
- repeated `/start` preserves existing timezone;
- `/timezone` command exists;
- valid timezone is saved;
- invalid timezone is rejected;
- timezone validation reuses domain helper from `DIREM-003`;
- handlers do not contain direct SQL queries;
- README lists `/timezone` as available;
- README does not claim reminder creation works;
- CHANGELOG includes user/timezone additions;
- existing `/start`, `/help`, `/version`, `/credits` still work;
- `python -m pytest` passes;
- `python -m compileall src alembic tests` passes;
- `docker compose config` passes;
- no reminder creation flow is implemented;
- no worker delivery logic is implemented;
- no out-of-scope dependencies are added.

---

## 10. Suggested verification commands

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
/timezone
Invalid/Zone
/version
/credits
```

Expected:

- `/start` responds and ensures user exists;
- valid timezone is saved;
- invalid timezone is rejected;
- version/credits remain stable.

---

## 11. Implementation guard

For Bushid Ronin V:

```text
Implement only DIREM-004 user registration and timezone flow.
Do not implement reminder creation, list, pause, resume, delete or worker delivery.
Keep handlers thin and call services.
Reuse DIREM-003 timezone validation.
Do not silently fallback to UTC for invalid user timezone input.
Do not add new infrastructure.
Preserve version and credits behavior.
```

---

## 12. Expected result summary

After this ticket:

```text
DIREM can persist Telegram users.
DIREM can persist a user's IANA timezone.
The bot still cannot create reminders.
The worker is still a stub.
Next ticket can safely implement reminder creation using the saved timezone.
```

