# DIREM-010 — Runtime Smoke & Release Readiness

## Status
Ready for implementation

## Version target
`DIREM v0.1.0 — Core MVP`

## Purpose

Prepare DIREM for real Telegram runtime smoke and v0.1.0 release readiness after Worker Delivery MVP.

This ticket should not add new product features.

## Scope

Need:

- document real Telegram runtime smoke checklist;
- separate automated required checks from optional runtime smoke;
- verify README truthfulness after worker delivery MVP;
- verify `.env.example` contains required configuration names but no secrets;
- document owner steps for creating/configuring a real Telegram bot;
- document expected runtime behavior:
  - `/start`
  - `/timezone`
  - `/new`
  - worker delivery
  - `/list`
  - `/pause`
  - `/resume`
  - `/delete`
- update CHANGELOG;
- preserve current MVP scope.

## Out of scope

Do not implement:

- retry scheduler;
- delivery history command;
- dashboard;
- webhook mode;
- Redis/Celery;
- AI features;
- inline buttons;
- reminder editing;
- new product commands;
- production deployment automation.

## Required automated checks

```bash
python -m pytest
python -m compileall src alembic tests
docker compose config
```

## Optional real Telegram runtime smoke

Run only when the owner has configured a real local `TELEGRAM_BOT_TOKEN`.

Owner checklist:

- create a Telegram bot through BotFather;
- copy `.env.example` to `.env`;
- put the real bot token into local `.env`;
- run `docker compose up --build`;
- run `docker compose run --rm bot alembic upgrade head`;
- send `/start`;
- set `/timezone` to `Asia/Almaty`;
- create a near-due reminder through `/new`;
- wait for worker delivery;
- check `/list` and verify `next_run_at` advanced;
- pause the reminder and ensure it is not delivered while paused;
- resume the reminder and ensure it can be delivered again;
- delete the reminder and verify it disappears from `/list`.

Expected readiness notes:

- worker delivery is basic MVP only;
- retries are not implemented;
- delivery history command is not implemented;
- dashboard and webhook mode are not implemented.
