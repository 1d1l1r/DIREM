# DIREM - Post-v0.2.0 Backlog

This backlog is a planning document. Nothing here is implemented until a dedicated ticket is accepted and merged.

## Shipped Through v0.2.0

These lines are historical context, not open backlog.

Released:

- `direm-v0.1.0` - Core MVP.
- `direm-v0.2.0` - Bunker and UX polish.

Notable shipped work:

- guided first-run onboarding;
- timezone picker UX and curated region picker;
- language and copy polish;
- Bunker Mode design and implementation;
- worker suppression while Bunker is active;
- home status screen and main menu hubs;
- README hero image and v0.2.0 release notes.

## Post-v0.2.0 Open Backlog

### Delivery History Command

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

### Retry Policy MVP

Purpose:
Handle failed Telegram sends more deliberately than logging and recording once.

Likely scope:
- retry eligibility rules;
- bounded retry attempts;
- tests for failed send behavior.

Out of scope:
- exponential backoff platform;
- Redis/Celery unless separately approved.

### Reminder Editing

Purpose:
Allow changing existing reminder title/message/schedule without delete-and-recreate.

Likely scope:
- edit selected reminder;
- preserve user isolation;
- recalculate `next_run_at` when schedule changes.

Out of scope:
- bulk editing;
- web UI.

### Reminder Details View

Purpose:
Show one reminder in a clearer focused view before heavier editing arrives.

Likely scope:
- select reminder by public number/id;
- show title, message, schedule, active window, status and next run.

Out of scope:
- editing;
- delivery history timeline.

## v0.3.0 - Response Check-ins / Reflection Foundation

### DIREM-031 - Response Check-ins Design

Purpose:
Design Response Check-ins as a separate DIREM domain concept before implementation.

Scope:
- define Reminder / Delivery / Check-in relationships;
- choose entity and table naming direction;
- define MVP response types;
- define Bunker and repeat-click behavior;
- split future implementation tickets.

Out of scope:
- migrations;
- Telegram callbacks;
- history command;
- text responses;
- snooze.

### DIREM-032 - Check-in Data Foundation

Purpose:
Add persistence for user responses to delivered reminders.

Likely scope:
- `ReminderCheckIn` model;
- `reminder_checkins` migration;
- response type constants;
- repository/service skeleton;
- schema and service tests.

Out of scope:
- worker delivery buttons;
- history command;
- text responses;
- snooze.

### DIREM-033 - Check-in Buttons MVP

Purpose:
Let a user mark a delivered reminder as done, later or skipped.

Likely scope:
- inline buttons on successful reminder deliveries;
- callback handler;
- user isolation;
- repeat-click behavior;
- localized confirmations.

Out of scope:
- changing reminder schedules;
- delivery history command;
- free-text response capture.

### DIREM-034 - Check-in History Command

Purpose:
Show recent reminder deliveries and user check-ins.

Likely scope:
- user-scoped history view;
- recent check-ins;
- delivery/check-in status display.

Out of scope:
- analytics dashboard;
- exports;
- AI summaries.

### DIREM-035 - Text Check-ins

Purpose:
Allow optional user-authored response text after a reminder delivery.

Likely scope:
- text capture flow;
- persistence in nullable response text;
- privacy/copy rules;
- tests for preserving user-authored content.

Out of scope:
- automatic translation;
- AI summarization;
- public sharing.

### DIREM-036 - Snooze / Later Scheduling

Purpose:
Define and implement real snooze behavior separately from the MVP `later` response.

Likely scope:
- explicit snooze choices;
- schedule mutation rules;
- no-catch-up-storm behavior;
- tests for next run calculation.

Out of scope:
- treating D031/D033 `later` as implicit snooze;
- retry scheduler;
- dashboard.

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
