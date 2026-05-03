# DIREM - Roadmap

## 0. Purpose

This document keeps DIREM's future work organized after the `direm-v0.2.0` release.

Roadmap entries are plans, not implemented features. Implementation still requires an active ticket, a branch, checks and review.

Current released state:

```text
direm-v0.2.0 - Bunker and UX polish
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

## 3. Completed Post-v0.1.0 Polish

Goal:

Make the released Core MVP easier to use without changing the product into a platform.

Shipped during the v0.2.0 cycle:

1. Guided first-run onboarding.
2. Timezone picker UX and curated region picker.
3. Russian/Kazakh/English copy polish after runtime usage.
4. Main menu and hub navigation.
5. Home status screen with user reminder stats.
6. Runtime smoke documentation refinements from owner testing.

Scope lock:

- No retries.
- No delivery history.
- No reminder editing.
- No dashboard/webhook.

## 4. Released: v0.2.0 - Bunker and UX Polish

Released as tag:

```text
direm-v0.2.0
```

Implemented:

- Bunker state foundation.
- Worker suppression for Bunker-active users.
- Telegram Bunker UX.
- Atomic Bunker exit rescheduling for active reminders.
- Home status and Bunker reply-keyboard toggle.
- Main menu navigation polish.
- Timezone picker v2 with curated regions.
- README hero image and v0.2.0 release docs.

Still not implemented:

- Delivery history command.
- Retry scheduler.
- Reminder editing.
- Reminder details view.
- Dashboard.
- Webhook mode.
- Redis/Celery unless a specific reliability ticket proves the need.
- AI translation.
- Web UI.

## 5. v0.3.0 - Response Check-ins / Reflection Foundation

Goal:

Let DIREM record how a user responded to delivered reminders while keeping reminder scheduling separate from response capture.

Candidate tickets:

1. Check-in data foundation.
2. Check-in buttons MVP for delivered reminders.
3. Check-in history command.
4. Text check-ins.
5. Snooze / Later scheduling as a separate feature after response capture is proven.

Scope lock:

- `later` is a recorded response, not snooze, until a dedicated snooze ticket is accepted.
- No analytics dashboard.
- No AI summaries.
- No task-manager completion model.
- No reminder editing unless covered by its own active ticket.

Expected release tag:

```text
direm-v0.3.0
```

## 6. Parked / Later

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

## 7. Candidate Version Sequence

```text
v0.1.0 - Core MVP - released
v0.2.0 - Bunker mode and UX polish - released
v0.3.0 - response check-ins and reflection foundation
v0.4.0 - delivery history, retries, editing
v0.5.0 - templates / rituals
v0.6.0 - project pulse
v1.0.0 - stable self-hosted release
```

The sequence can change after real usage. If a bug blocks daily use, it should become a patch ticket before larger features.
