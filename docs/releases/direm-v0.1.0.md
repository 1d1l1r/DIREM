# DIREM v0.1.0 - Core MVP

Release date: 2026-04-29

## Summary

DIREM v0.1.0 is the first Core MVP release of the Telegram-first reminder system. It includes the runnable bot and worker services, persisted reminder records, timezone-aware scheduling, basic worker delivery, and Russian, Kazakh and English interface language support.

## Added

- Telegram bot commands: `/start`, `/help`, `/language`, `/timezone`, `/new`, `/list`, `/pause`, `/resume`, `/delete`, `/version`, `/credits` and `/cancel`.
- PostgreSQL schema and SQLAlchemy models for users, reminders, reminder deliveries and user states.
- Alembic migrations through `20260429_003_user_language`.
- Pure domain schedule calculation for interval and daily reminders.
- User timezone persistence with IANA timezone validation.
- Per-user interface language selection for Russian, Kazakh and English.
- Reminder creation, listing, pause, resume and delete flows for the current Telegram user.
- Inline reminder control buttons for pause, resume and delete confirmation.
- Localized Help/Cancel reply keyboard behavior.
- Worker delivery MVP for due active reminders with sent/failed delivery records.
- Centralized `/version` and `/credits` metadata.
- Runtime smoke checklist for owner-operated Telegram verification.

## Known Limitations

- No retry scheduler.
- No delivery history command.
- No delivery dashboard.
- No webhook mode.
- No AI translation.
- No reminder editing.
- No web UI.
- Worker delivery is a basic MVP, not production-grade observability or retry infrastructure.
- User-authored reminder title and message text are not auto-translated.

## Checks

- `python -m pytest` -> 110 passed.
- `python -m compileall src alembic tests` -> passed.
- `docker compose config` -> passed.
- `docker compose run --rm bot alembic heads` -> `20260429_003_user_language (head)`.
- `docker compose run --rm bot alembic current` -> `20260429_003_user_language (head)`.
- `docker compose run --rm bot alembic upgrade head` -> passed.
- `docker compose run --rm bot alembic current` -> `20260429_003_user_language (head)`.

## Credits

- Project direction: 1D1L1R
- Architecture, scope lock and review: Rein Hard V
- Implementation and release execution: Bushid Ronin V

Credits preserved:
1D1L1R · Rein Hard V · Bushid Ronin V
