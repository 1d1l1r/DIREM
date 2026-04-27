# DIREM-011 — Runtime Smoke: Fix `/new` Confirmation Session Injection

## Status
Ready for implementation

## Version target
`DIREM v0.1.0 — Core MVP`

## Purpose

Fix the first real Telegram runtime smoke blocker: `/new` reaches the final confirmation/create step, then crashes because the confirmation handler does not receive a database session.

This is a bugfix-only ticket. It must not add new product features.

## Runtime evidence

During real Telegram runtime smoke, the bot reaches `/new` confirmation/create stage.

After pressing/sending final create confirmation, the bot crashes with:

```text
TypeError: confirm_create() missing 1 required positional argument: 'session'

Trace shows aiogram calling confirm_create without injected session.

Observed secondary worker issue:

relation "reminders" does not exist

This happened because worker started polling before migrations were applied. This is secondary and should not distract from the primary /new blocker.

Context

Already implemented:

DIREM-001 — project skeleton
DIREM-002 — domain model / database schema
DIREM-003 — schedule calculation domain
DIREM-004 — user registration + /timezone
DIREM-005 — /new reminder creation flow
DIREM-006 — /list reminder viewing flow
DIREM-007 — /pause and /resume
DIREM-008 — /delete
DIREM-009 — worker delivery MVP
DIREM-010 — runtime smoke / release readiness checklist

Current behavior:

bot starts and responds to earlier commands;
/new flow proceeds through earlier FSM steps;
final confirmation/create crashes;
reminder is not created;
worker delivery smoke cannot be completed until /new works in real Telegram runtime.
Scope

Implement only the bugfix for /new final confirmation/create path.

Need:

inspect src/direm/bot/handlers/new.py;
inspect confirm_create handler signature;
inspect DB session middleware injection contract;
verify whether DB session middleware is attached to the router containing /new;
verify whether handler parameter name matches middleware data key;
fix session injection or adjust handler/service wiring according to existing project architecture;
ensure final create path persists reminder successfully;
ensure FSM state clears after successful creation;
ensure created reminder appears in /list;
add regression test if project test style allows it;
add or update tests for confirmation/create path;
update README/RUNTIME_SMOKE only if expected owner input needs clarification;
update CHANGELOG.
Secondary worker startup note

Worker currently can start before migrations and log:

relation "reminders" does not exist

Do not build a full migration runner.

Allowed:

document clearly that migrations must be applied before runtime smoke;
or make a small safe worker guard/log improvement if it is minimal and does not expand scope.

Not required:

deployment automation;
automatic migrations;
production-grade startup orchestration.
Out of scope

Do not implement:

new product features;
retry scheduler;
delivery history command;
dashboard;
webhook mode;
Redis/Celery;
AI features;
inline buttons;
reminder editing;
large router/middleware refactor;
automatic migration runner.
Acceptance criteria
/new final confirmation no longer crashes;
bot replies with successful reminder creation;
reminder is persisted;
FSM state is cleared after creation;
/list shows the newly created reminder;
automated tests pass;
README/RUNTIME_SMOKE remain truthful;
CHANGELOG mentions the runtime smoke bugfix;
no new product scope is introduced.
Required checks
python -m pytest
python -m compileall src alembic tests
docker compose config
Optional owner runtime smoke

Only if real Telegram bot token is configured locally.

docker compose down
docker compose up --build
docker compose run --rm bot alembic upgrade head
docker compose restart bot worker

Then in Telegram:

/start
/timezone
Asia/Almaty
/new
/list

Expected:

/new completes successfully;
reminder is created;
/list shows the reminder;
bot logs do not show confirm_create() missing session;
worker logs do not repeatedly show missing table errors after migrations.

А Ронину можно коротко сверху дать:

```text
Bushid Ronin V, создай и выполни тикет:

`docs/tickets/DIREM-011-runtime-smoke-new-confirm-session-fix.md`

Bugfix only. Главный blocker из runtime smoke:

`TypeError: confirm_create() missing 1 required positional argument: 'session'`

Сначала дай plan + expected changed files, потом реализация.