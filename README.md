# DIREM

DIREM is a Telegram-first system for regular returns to intention.

Current target: `DIREM v0.1.0 — Core MVP`.

This repository currently contains the DIREM Core MVP: bot service, worker delivery MVP, PostgreSQL, SQLAlchemy 2, Alembic, version metadata, credits metadata, user registration, persisted user timezones and languages, `/new` reminder record creation, `/list` reminder record viewing, `/pause` and `/resume` status updates, `/delete` reminder record deletion, domain constants, database models for users/reminders/deliveries/user states, and tested schedule calculation functions.

Reminder delivery is now implemented as a basic MVP: the worker polls for due active reminders, sends them to the user's persisted Telegram chat, records success or failure, and advances `next_run_at` after successful sends. Retries, delivery history commands, dashboards and webhook mode are intentionally not implemented.

## Stack

- Python 3.12
- aiogram 3
- PostgreSQL
- SQLAlchemy 2
- Alembic
- Docker Compose

## Configuration

Copy the safe example file and fill only local secrets:

```bash
cp .env.example .env
```

Required values:

- `TELEGRAM_BOT_TOKEN`
- `DATABASE_URL`
- `DIREM_ENV`
- `DIREM_VERSION`
- `DIREM_COMMIT_SHA`
- `DIREM_BUILD_DATE`

The real `.env` file is ignored by git.

## Run

```bash
docker compose up --build
```

Services:

- `db` — PostgreSQL
- `bot` — runs `python -m direm.bot.main`
- `worker` — runs `python -m direm.worker.main`

The worker runs a basic polling delivery loop for due active reminders.

## Migrations

Run migrations after the database is healthy:

```bash
docker compose run --rm bot alembic upgrade head
```

The migrations create the schema foundation:

- `users`
- `reminders`
- `reminder_deliveries`
- `user_states`

These tables support persisted reminder creation and basic worker delivery records.

## Bot Commands

Available in this Core MVP:

- `/start`
- `/help`
- `/language`
- `/timezone`
- `/new`
- `/list`
- `/pause`
- `/resume`
- `/delete`
- `/version`
- `/credits`
- `/cancel`

Not implemented yet:

- retry scheduler
- AI translation
- delivery history command
- delivery dashboard
- webhook mode
- reminder editing

Implemented as schema foundation only:

- `Reminder` SQLAlchemy model
- `ReminderDelivery` SQLAlchemy model
- `UserState` SQLAlchemy model
- domain constants for schedule, reminder and delivery statuses
- repository skeletons, with `ReminderRepository` create/list/status-update/delete operations wired for current MVP flows

Implemented as pure domain logic only:

- timezone validation with IANA timezone names
- active window validation and checks
- interval and daily next-run calculation
- no catch-up storm helper for worker delivery use

These functions are tested and used by `/new` and the worker delivery MVP to calculate `next_run_at`.

Implemented as persisted user setup:

- `/start` creates or updates a Telegram user record
- repeated `/start` preserves the existing timezone
- `/timezone` stores a validated IANA timezone such as `Asia/Almaty`
- `/language` stores a selected interface language

Users can now persist an IANA timezone and interface language. Supported interface languages are Russian, Kazakh and English. User-authored reminder titles and message text are not auto-translated.

Implemented reminder creation:

- `/new` creates interval or daily reminder records
- optional same-day active windows are supported
- `next_run_at` is calculated and stored in UTC
- `/list` shows the current user's reminder records with local `next_run_at`
- `/pause` marks active reminders as paused using inline buttons or manual number/id input
- `/resume` marks paused reminders as active and recalculates `next_run_at` using inline buttons or manual number/id input
- `/delete` deletes reminder records for the current Telegram user after confirmation, using inline buttons or manual number/id input

Implemented worker delivery MVP:

- worker polls due active reminders where `next_run_at <= now`
- paused and deleted reminders are skipped
- messages are sent to the persisted Telegram `chat_id`
- successful sends create `reminder_deliveries` records
- failed sends are logged and recorded without crashing the worker
- successful sends advance `next_run_at` using the user's timezone and domain schedule functions
- delivery message wrapper text uses the user's selected interface language

Retries, AI translation, delivery history commands, dashboards, webhook mode and reminder editing are still not implemented.

## Release Readiness

Required automated checks:

```bash
python -m pytest
python -m compileall src alembic tests
docker compose config
```

Optional real Telegram runtime smoke depends on an owner-configured real `TELEGRAM_BOT_TOKEN`. See [docs/RUNTIME_SMOKE.md](docs/RUNTIME_SMOKE.md).

Runtime smoke summary:

1. Create a bot through BotFather.
2. Copy `.env.example` to `.env`.
3. Put the real bot token into local `.env`.
4. Run `docker compose up --build`.
5. Run `docker compose run --rm bot alembic upgrade head`.
6. Restart runtime services after migrations: `docker compose restart bot worker`.
7. Send `/start`.
8. Check that Telegram shows the command menu with `/language` and `/cancel`.
9. Send `/language`, choose Қазақша, then verify `/help` is in Kazakh.
10. Send `/language`, choose English, then verify `/help` is in English.
11. Send `/language`, choose Русский, then verify `/help` is in Russian.
12. Start `/new`, verify the localized Cancel reply button appears, tap it and verify the flow exits.
13. Set `/timezone` to `Asia/Almaty`.
14. Create a near-due reminder through `/new`.
15. Wait for worker delivery.
16. Check `/list` and verify `next_run_at` advanced.
17. Use `/pause`, tap an inline reminder button, then verify `/list` shows it paused.
18. Use `/resume`, tap an inline reminder button, then verify `/list` shows it active.
19. Use `/delete`, tap a reminder button, cancel once, then repeat and confirm deletion.
20. Verify the deleted reminder disappears from `/list`.

Expected:

- bot answers available shell and setup commands;
- Telegram command menu shows current commands including `/language` and `/cancel`;
- `/language` changes persisted interface language between Russian, Kazakh and English;
- reminder title/message text is not auto-translated;
- `/cancel` exits active FSM flows and is friendly when nothing is active;
- `/new` can create a reminder record;
- `/list` shows reminder records for the current Telegram user;
- `/pause` and `/resume` inline buttons update reminder status for the current Telegram user;
- `/delete` inline confirmation removes reminder records from the current Telegram user's list;
- worker sends due active reminders with basic MVP delivery behavior;
- worker does not implement retries, delivery history commands, dashboards or webhook mode;
- db container stays healthy;
- logs do not print the Telegram token.

## Credits

Project Owner:
- 1D1L1R

Co-authors:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — implementation executor
