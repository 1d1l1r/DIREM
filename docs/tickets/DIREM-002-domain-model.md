# DIREM-002 — Domain Model

## Status

Accepted

## Version target

```text
DIREM v0.1.0 — Core MVP
```

## Owner / Coauthors

Use canonical credits from `docs/COAUTHORS.md` and README.

---

## 1. Purpose

Implement the database schema foundation for DIREM domain entities.

This ticket adds SQLAlchemy models, Alembic schema migration, domain constants and repository skeletons for reminders, deliveries and user states.

This ticket does **not** implement Telegram reminder flows, schedule calculation, worker delivery or repository wiring.

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
ADR-002 — Use PostgreSQL + SQLAlchemy 2 + Alembic
ADR-003 — Split bot service and worker service
ADR-004 — Store timestamps in UTC, interpret user schedules via IANA timezones
ADR-011 — Use simple polling worker, no external queue in MVP
ADR-014 — Keep MVP single-user friendly but multi-user capable
```

---

## 3. Scope

### In scope

- SQLAlchemy model `Reminder`;
- SQLAlchemy model `ReminderDelivery`;
- SQLAlchemy model `UserState`;
- Alembic migration for `reminders`, `reminder_deliveries`, `user_states`;
- domain constants/enums for schedule types, reminder statuses and delivery statuses;
- repository skeletons for users, reminders, deliveries and user states;
- minimal tests for constants and schema metadata;
- README/CHANGELOG updates.

### Out of scope

Do **not** implement:

- Telegram `/new`;
- `/list`, `/pause`, `/resume`, `/delete`;
- `/timezone` flow;
- schedule calculation;
- worker due reminder logic;
- delivery sending;
- Redis/Celery;
- web dashboard;
- webhook mode;
- AI features.

---

## 4. Acceptance checklist

This ticket is complete when:

- domain constants exist and are tested;
- SQLAlchemy metadata contains `reminders`, `reminder_deliveries`, `user_states`;
- Alembic migration creates the new domain tables;
- repository skeletons exist without business logic;
- README says the schema foundation exists but creation/delivery are not wired;
- CHANGELOG records the schema foundation;
- no Telegram reminder flows are added;
- no worker delivery logic is added;
- no out-of-scope dependencies are added;
- `python -m pytest` passes;
- `python -m compileall src alembic tests` passes;
- `docker compose config` passes.

---

## 5. Implementation guard

```text
Implement only DIREM-002 domain model and database schema foundation.
Do not implement schedule calculation.
Do not implement Telegram reminder creation or worker delivery.
Keep repository classes as skeletons only.
Preserve canonical credits.
```
