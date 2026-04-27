# DIREM-001 — Project Skeleton

## Status

Ready for implementation

## Version target

```text
DIREM v0.1.0 — Core MVP
```

## Owner / Coauthors

```text
Project Owner:
- 1D1L1R

Co-authors:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — implementation executor
```

---

## 1. Purpose

Create the initial DIREM repository skeleton for a self-hosted Telegram-first reminder system.

This ticket does **not** implement reminder creation, scheduling, worker delivery logic, or real Telegram flows beyond minimal bootstrapping/stubs.

The goal is to establish:

- Python project structure;
- Docker Compose runtime;
- PostgreSQL service;
- Alembic migration baseline;
- aiogram bot entrypoint;
- worker entrypoint stub;
- configuration loading;
- version metadata;
- credits metadata;
- README startup instructions;
- safe `.env.example`;
- initial changelog.

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
ADR-001 — Use Python 3.12 + aiogram 3
ADR-002 — Use PostgreSQL + SQLAlchemy 2 + Alembic
ADR-003 — Split bot service and worker service
ADR-005 — Use polling mode for MVP
ADR-009 — Keep version and credits visible from MVP
ADR-011 — Use simple polling worker, no external queue in MVP
```

---

## 3. Scope

### In scope

Implement initial skeleton:

- `pyproject.toml`;
- `Dockerfile`;
- `docker-compose.yml`;
- `.env.example`;
- `.gitignore` if missing;
- `README.md` baseline;
- `CHANGELOG.md` baseline;
- Python package under `src/direm/`;
- config module;
- logging module;
- version metadata module;
- credits metadata module;
- bot entrypoint;
- worker entrypoint stub;
- database session/config baseline;
- SQLAlchemy base/models placeholder;
- Alembic baseline setup;
- first migration for minimal `users` table if practical;
- `/version` command stub;
- `/credits` command stub;
- `/start` and `/help` minimal stubs;
- basic smoke notes in README.

### Out of scope

Do **not** implement:

- reminder creation flow;
- `/new`;
- `/list`;
- `/pause`;
- `/resume`;
- `/delete`;
- `/timezone` flow;
- real worker due reminder logic;
- reminder deliveries;
- active window calculation;
- schedule calculation;
- AI generation;
- web dashboard;
- Telegram WebApp;
- Redis/Celery;
- webhook mode;
- ReMemBear mascot/stickers;
- legacy PHP port.

---

## 4. Required project structure

Create or align with this structure:

```text
src/
  direm/
    __init__.py

    app/
      __init__.py
      config.py
      logging.py
      version.py
      credits.py

    bot/
      __init__.py
      main.py
      router.py
      handlers/
        __init__.py
        start.py
        help.py
        version.py
        credits.py

    worker/
      __init__.py
      main.py
      loop.py

    db/
      __init__.py
      base.py
      models.py
      session.py

    services/
      __init__.py
      version_service.py
      credits_service.py

alembic/
  versions/

tests/
  unit/
```

If the exact structure must differ for a good technical reason, keep the same separation:

```text
app / bot / worker / db / services
```

---

## 5. Dependencies

Use Python 3.12.

Minimum dependencies:

```text
aiogram 3.x
SQLAlchemy 2.x
asyncpg
alembic
pydantic-settings or equivalent config loader
python-dotenv if needed
pytest
pytest-asyncio if needed
```

Do not add unnecessary dependencies.

Do not add Redis, Celery, FastAPI, frontend tooling, or dashboard dependencies in this ticket.

---

## 6. Configuration

Create `.env.example` with safe placeholders only:

```text
DIREM_ENV=local
DIREM_VERSION=0.1.0
DIREM_COMMIT_SHA=unknown
DIREM_BUILD_DATE=unknown

TELEGRAM_BOT_TOKEN=replace_me

POSTGRES_DB=direm
POSTGRES_USER=direm
POSTGRES_PASSWORD=direm
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://direm:direm@db:5432/direm

WORKER_POLL_SECONDS=10
WORKER_BATCH_SIZE=20

LOG_LEVEL=INFO
```

Rules:

- real `.env` must be gitignored;
- missing `TELEGRAM_BOT_TOKEN` should fail clearly when starting the bot;
- `/version` must not expose secrets;
- never log `TELEGRAM_BOT_TOKEN`.

---

## 7. Docker Compose

Create `docker-compose.yml` with at least:

```text
bot
worker
db
```

Expected behavior:

- `bot` runs `python -m direm.bot.main`;
- `worker` runs `python -m direm.worker.main`;
- `db` uses PostgreSQL;
- both `bot` and `worker` use the same image/build context;
- database data is persisted in a named Docker volume;
- env vars are loaded from `.env` or compose environment.

Worker may only log a heartbeat/stub message in this ticket.

---

## 8. Bot commands required in this ticket

Implement minimal working handlers:

### `/start`

Can respond with a short DIREM introduction.

Does not need full user registration yet unless trivial to include with the initial users table.

### `/help`

Shows available MVP/planned commands, but marks only current commands as available if needed.

### `/version`

Uses centralized version metadata.

Expected format:

```text
DIREM v0.1.0
Commit: unknown
Build: unknown
Environment: local
DB migration: unknown
```

DB migration may be `unknown` in this ticket if revision reading is not implemented yet.

### `/credits`

Uses centralized credits metadata.

Expected text:

```text
DIREM credits

Project Owner:
- 1D1L1R

Co-authors:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — implementation executor
```

---

## 9. Version and credits metadata

Create centralized metadata modules/services.

Example:

```text
src/direm/app/version.py
src/direm/app/credits.py
src/direm/services/version_service.py
src/direm/services/credits_service.py
```

Requirements:

- `/version` should not hardcode all text inside handler;
- `/credits` should not hardcode all text inside handler;
- missing metadata falls back to `unknown`;
- coauthor names must match `docs/COAUTHORS.md` exactly.

---

## 10. Database and Alembic

Set up SQLAlchemy and Alembic baseline.

Minimum acceptable result:

- DB session/config exists;
- Alembic is configured;
- migrations directory exists;
- README explains how to run migrations.

Preferred result:

- initial migration creates `users` table.

Minimal `users` table:

```text
id
telegram_user_id
chat_id
username
first_name
timezone
created_at
updated_at
```

If implementing the users table creates too much scope, leave a clear TODO and keep Alembic ready.

Do not implement reminders table in this ticket unless it is necessary for migration sanity. Reminder tables belong to the next domain/model ticket.

---

## 11. README baseline

Create/update `README.md` with:

- what DIREM is;
- current version target;
- stack summary;
- required environment variables;
- local run steps;
- Docker Compose commands;
- migration command;
- basic smoke test steps;
- credits section.

Minimum commands to document:

```bash
cp .env.example .env
docker compose up --build
```

If migrations require a separate command, document it.

---

## 12. CHANGELOG baseline

Create `CHANGELOG.md`:

```markdown
# Changelog

## [0.1.0] - Unreleased

### Added
- Initial DIREM project skeleton.
- Docker Compose baseline with bot, worker and PostgreSQL services.
- Version and credits metadata stubs.
```

---

## 13. Tests

Add minimal tests if practical:

- version metadata fallback test;
- credits metadata contains required names;
- config loads safe defaults or test env.

Do not spend this ticket on broad integration tests.

---

## 14. Acceptance checklist

This ticket is complete when:

- project has Python package under `src/direm`;
- `pyproject.toml` exists;
- Dockerfile exists;
- `docker-compose.yml` defines `bot`, `worker`, `db`;
- `.env.example` exists and contains no real secrets;
- `.env` is gitignored;
- bot entrypoint exists;
- worker entrypoint exists and can start as a stub;
- app config loads from environment;
- `/start` handler exists;
- `/help` handler exists;
- `/version` handler exists;
- `/credits` handler exists;
- version metadata uses fallback `unknown`;
- credits include 1D1L1R, Rein Hard V and Bushid Ronin V;
- Alembic baseline exists;
- README explains local startup;
- CHANGELOG has `0.1.0 - Unreleased` entry;
- no reminder business logic is implemented yet;
- no legacy PHP code is ported or referenced as runtime code;
- no out-of-scope dependencies are added.

---

## 15. Suggested smoke test

After implementation:

```bash
cp .env.example .env
# fill TELEGRAM_BOT_TOKEN in .env

docker compose up --build
```

Then in Telegram:

```text
/start
/help
/version
/credits
```

Expected:

- bot responds to all four commands;
- worker starts and logs stub heartbeat or idle loop;
- db container stays healthy;
- no secrets are printed in logs.

---

## 16. Implementation guard

For Bushid Ronin V:

```text
Read docs/CONCEPT.md, docs/PRODUCT_SCOPE.md, docs/ARCHITECTURE.md, docs/VERSIONING.md, docs/COAUTHORS.md, docs/ROADMAP.md and docs/DECISIONS.md before implementation.
Implement only DIREM-001 project skeleton.
Do not implement reminders, schedule calculation, delivery worker logic, web dashboard, AI features, Redis/Celery, webhook mode, mascot/stickers, or legacy PHP porting.
Keep handlers thin.
Centralize version and credits metadata.
Preserve coauthor names exactly.
Prefer simple, boring, testable structure.
```

---

## 17. Expected result summary

After this ticket, the repository should be a runnable DIREM shell:

```text
Docker Compose starts bot + worker + db.
Bot can answer /start, /help,