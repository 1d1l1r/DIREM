# DIREM - Roadmap

## 0. Purpose

This document keeps DIREM's future work organized after the `direm-v0.1.0` Core MVP release.

Roadmap entries are plans, not implemented features. Implementation still requires an active ticket, a branch, checks and review.

Current released state:

```text
direm-v0.1.0 - Core MVP
```

## 1. Roadmap Guard

- Do not implement roadmap items without an active ticket.
- Keep docs honest: planned means planned, not shipped.
- Prefer small post-release tickets over large mixed branches.
- New product behavior starts from a new branch off `main`.
- Dashboard, webhook, Redis/Celery, AI translation and web UI remain parked until explicitly activated.

## 2. Released: v0.1.0 - Core MVP

Released as tag:

```text
direm-v0.1.0
```

Implemented:

- Telegram bot service and worker service.
- PostgreSQL, SQLAlchemy 2 and Alembic migrations.
- `/start`, `/help`, `/language`, `/timezone`, `/new`, `/list`, `/pause`, `/resume`, `/delete`, `/version`, `/credits` and `/cancel`.
- Reminder creation, list, pause, resume and delete flows for the current Telegram user.
- Worker delivery MVP for due active reminders.
- Delivery records for successful and failed send attempts.
- IANA timezone validation and persisted user timezone.
- Russian, Kazakh and English interface language selection.
- Localized Help/Cancel reply keyboard behavior.
- Inline reminder control buttons.
- Runtime smoke checklist and release notes.

Still not implemented:

- Guided first-run onboarding.
- Timezone picker UX.
- Delivery history command.
- Retry scheduler.
- Reminder editing.
- Dashboard.
- Webhook mode.
- AI translation.
- Web UI.

## 3. v0.1.1 - Polish / UX / Small Fixes

Goal:

Make the released Core MVP easier to use without changing the data model or adding broad new infrastructure.

Candidate tickets:

1. Guided first-run onboarding.
2. Timezone picker UX.
3. Russian/Kazakh/English copy polish after real usage.
4. Empty state and confirmation copy polish.
5. Runtime smoke documentation refinements from owner testing.
6. Bunker Mode design.

Scope lock:

- No retries.
- No delivery history.
- No reminder editing.
- No dashboard/webhook.
- No migrations unless a small bug fix truly requires one.

Expected release tag:

```text
direm-v0.1.1
```

## 4. v0.2.0 - Functional Expansion

Goal:

Add the first post-MVP functional capabilities while keeping the Telegram-only product shape.

Candidate tickets:

1. Bunker Mode implementation.
2. Delivery history command.
3. Retry policy MVP.
4. Reminder editing.
5. Reminder details view.
6. Safer worker observability and owner-readable diagnostics.

Scope lock:

- No dashboard.
- No webhook mode.
- No Redis/Celery unless a specific reliability ticket proves the need.
- No AI translation.
- No web UI.

Expected release tag:

```text
direm-v0.2.0
```

## 5. Parked / Later

These ideas are saved but not scheduled for the next release lanes.

### Dashboard / Web UI

Possible later direction:

- Telegram WebApp or separate web dashboard.
- Visual reminder list and editing.
- Delivery history view.

Not now because Telegram-only usage should prove its limits first.

### Bunker Mode Extensions

Possible later direction:

- timed Bunker until a selected date/time;
- Bunker status display in reminder lists;
- owner diagnostics for suppressed reminders.

Not in the first Bunker implementation because the initial design keeps Bunker as simple user-level delivery suppression.

### Webhook Mode

Possible later direction:

- Webhook deployment mode for hosted environments.

Not now because polling is simpler and good enough for the self-hosted MVP.

### Redis / Celery

Possible later direction:

- Dedicated queue and retry infrastructure.

Not now because the current worker is intentionally small and easier to inspect.

### AI Translation / Generated Copy

Possible later direction:

- Optional generated reminder phrasing.
- Optional interface copy assistance.

Not now because user-authored reminder title/message content must stay stable and unmodified.

### Voice / Audio

Possible later direction:

- Voice notes or audio reminders.

Not now because it changes the product surface and operational complexity.

## 6. Candidate Version Sequence

```text
v0.1.0 - Core MVP - released
v0.1.1 - UX polish and small fixes
v0.2.0 - delivery history, retries, editing
v0.3.0 - templates / rituals
v0.4.0 - reflection and response history
v0.5.0 - project pulse
v1.0.0 - stable self-hosted release
```

The sequence can change after real usage. If a bug blocks daily use, it should become a patch ticket before larger features.
