# DIREM-016 - Pre-release Telegram UX Polish

## Status

Implemented

## Version target

`DIREM v0.1.0 - Core MVP`

## Purpose

Polish the Telegram user experience before the v0.1.0 release without adding new product features.

## Scope

- Rewrite `/help` into user-facing grouped sections.
- Remove technical worker/retries/dashboard/webhook notes from Telegram `/help`.
- Keep technical limitations in README/CHANGELOG only.
- Localize updated `/help` for Russian, Kazakh and English.
- Add a default reply keyboard:
  - idle users see localized Help;
  - users in active FSM flows see localized Cancel.
- Make Help and Cancel reply buttons behave like `/help` and `/cancel`.
- Preserve existing inline buttons for `/language`, `/pause`, `/resume` and `/delete`.
- Update runtime smoke documentation and tests.

## Out of scope

- Guided onboarding after `/start`.
- Timezone picker by country/continent/GMT.
- New reminder features.
- Reminder editing.
- Retries.
- Delivery history command.
- Dashboard/webhook.
- Redis/Celery/AI.
- Web UI.
- Broad redesign.

## Checks

- `python -m pytest`
- `python -m compileall src alembic tests`
- `docker compose config`
