# DIREM - Post-v0.1.0 Backlog

This backlog is a planning document. Nothing here is implemented until a dedicated ticket is accepted and merged.

## v0.1.1 - Polish / UX / Small Fixes

### DIREM-019 - Guided First-run Onboarding

Purpose:
Help a new user understand the shortest useful path after `/start`.

Likely scope:
- friendly first-run text;
- point to `/language`, `/timezone` and `/new`;
- avoid a heavy tutorial.

Out of scope:
- onboarding state machine unless strictly needed;
- new reminder features.

### DIREM-020 - Timezone Picker UX

Purpose:
Reduce friction for users who do not know IANA timezone names.

Likely scope:
- guided examples;
- common timezone shortcuts;
- better invalid timezone recovery.

Out of scope:
- full country/continent browser unless explicitly approved;
- automatic timezone detection.

### DIREM-021 - Language and Copy Polish

Purpose:
Polish Russian, Kazakh and English user-facing copy after real runtime usage.

Likely scope:
- `/help`;
- `/new`;
- `/timezone`;
- control flow prompts;
- worker delivery wrapper.

Out of scope:
- AI translation;
- automatic translation of user-authored reminder content.

### DIREM-022 - Empty States and Confirmation Polish

Purpose:
Make empty lists, invalid choices and confirmation screens clearer.

Likely scope:
- `/list` empty state;
- `/pause`, `/resume`, `/delete` empty states;
- stale callback copy;
- confirmation wording.

Out of scope:
- new commands;
- reminder editing.

### DIREM-023 - Bunker Mode Design

Purpose:
Design user-level Bunker Mode before implementation.

Scope:
- define activation/deactivation behavior;
- define worker suppression behavior;
- define reminder state restore semantics;
- recommend data model and migration direction.

Out of scope:
- `/bunker` command;
- migrations;
- worker changes;
- runtime implementation.

## v0.2.0 - Functional Expansion

### Bunker Mode Implementation

Purpose:
Let a user temporarily silence all DIREM reminder delivery without rewriting individual reminder statuses.

Likely scope:
- user-level Bunker state;
- worker suppression;
- Telegram UX;
- active reminder `next_run_at` recalculation on exit.

Out of scope:
- timed Bunker;
- per-reminder snooze;
- dashboard or analytics.

### DIREM-024 - Delivery History Command

Purpose:
Let a user inspect recent reminder delivery events.

Likely scope:
- `/history` or equivalent command;
- show recent sent/failed delivery records;
- current Telegram user isolation.

Out of scope:
- dashboard;
- analytics;
- exports.

### DIREM-025 - Retry Policy MVP

Purpose:
Handle failed Telegram sends more deliberately than logging and recording once.

Likely scope:
- retry eligibility rules;
- bounded retry attempts;
- tests for failed send behavior.

Out of scope:
- exponential backoff platform;
- Redis/Celery unless separately approved.

### DIREM-026 - Reminder Editing

Purpose:
Allow changing existing reminder title/message/schedule without delete-and-recreate.

Likely scope:
- edit selected reminder;
- preserve user isolation;
- recalculate `next_run_at` when schedule changes.

Out of scope:
- bulk editing;
- web UI.

### DIREM-027 - Reminder Details View

Purpose:
Show one reminder in a clearer focused view before heavier editing arrives.

Likely scope:
- select reminder by public number/id;
- show title, message, schedule, active window, status and next run.

Out of scope:
- editing;
- delivery history timeline.

## Parked / Later

- Dashboard or Telegram WebApp.
- Webhook mode.
- Redis/Celery queue infrastructure.
- AI translation or generated reminder text.
- Voice/audio features.
- Public SaaS mode.
- Team/shared reminder spaces.

## Backlog Guard

- Backlog items are not permission to implement.
- Every item needs a dedicated ticket and branch.
- Keep v0.1.1 small unless runtime usage proves a blocker.
- Keep v0.2.0 focused on useful reminder operation, not platform expansion.
