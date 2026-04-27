# DIREM-013 — Telegram Command Menu and Cancel Flow

## Status
Ready for implementation

## Version target
`DIREM v0.1.0 — Core MVP`

## Purpose

Polish Telegram UX before adding more product features.

DIREM already has the Core MVP command set and worker delivery MVP. This ticket makes the bot easier and safer to use in real Telegram runtime.

## Scope

Need:

- register Telegram command menu via `set_my_commands`;
- include current MVP commands:
  - `/start`
  - `/help`
  - `/timezone`
  - `/new`
  - `/list`
  - `/pause`
  - `/resume`
  - `/delete`
  - `/version`
  - `/credits`
  - `/cancel`
- add `/cancel` command;
- `/cancel` clears current FSM state;
- `/cancel` works during:
  - `/timezone`
  - `/new`
  - `/pause`
  - `/resume`
  - `/delete`
- if there is no active FSM state, `/cancel` replies with a friendly message;
- update `/help`;
- ensure invalid input in active flows gives a user-facing response where practical;
- update README;
- update RUNTIME_SMOKE if needed;
- update CHANGELOG;
- add tests.

## Out of scope

Do not implement:

- language selection;
- i18n foundation;
- inline reminder selection buttons;
- new reminder features;
- reminder editing;
- retry scheduler;
- delivery history command;
- dashboard;
- webhook mode;
- Redis/Celery;
- AI features;
- web UI.

## Acceptance criteria

- Telegram command menu contains all current MVP commands;
- `/cancel` clears active FSM state;
- `/cancel` does not crash when no FSM state exists;
- `/help` matches current commands;
- invalid FSM input does not look like silent hang where practical;
- existing flows still work;
- README and CHANGELOG remain truthful;
- tests pass.

## Required checks

```bash
python -m pytest
python -m compileall src alembic tests
docker compose config
Optional runtime smoke

Only if real Telegram bot token is configured:

/start
check Telegram command menu
/new
/cancel
/list
/timezone
/cancel

Expected:

command menu is visible;
/cancel exits active flows;
bot does not silently hang on cancelled flows.