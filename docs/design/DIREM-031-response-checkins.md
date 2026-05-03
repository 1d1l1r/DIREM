# DIREM-031 - Response Check-ins Design

## Status

Accepted design direction for future implementation. Response Check-ins are not implemented by this document.

## Purpose

Response Check-ins add a small response layer after DIREM delivers a reminder.

The goal is to let a user mark what happened after a delivered ping without turning DIREM into a task manager, habit tracker or analytics dashboard.

Core split:

```text
Reminder = recurring intention rule and schedule
Delivery = one concrete send attempt for a reminder
Check-in = user's response to a delivered reminder
```

Example:

```text
Reminder
- title: Morning focus
- schedule: every 60 minutes

Delivery
- sent_at: 2026-05-03 10:00 UTC
- status: sent

ReminderCheckIn
- response_type: done
- responded_at: 2026-05-03 10:04 UTC
```

## Entity Naming

Recommended domain entity:

```text
ReminderCheckIn
```

Recommended table:

```text
reminder_checkins
```

Reasoning:

- `ReminderCheckIn` keeps the concept tied to the reminder domain.
- It avoids generic `Response`, which may later conflict with API or Telegram response language.
- It avoids `Task`, `Assignment` or `Completion`, which would pull DIREM toward task-manager semantics.
- UI copy can still use softer words such as "response", "mark", "check-in" or "reaction".

## Relationship Model

Recommended relationship:

```text
users 1--N reminder_checkins
reminders 1--N reminder_checkins
reminder_deliveries 1--0/1 reminder_checkins
```

Each MVP check-in should link to:

- `user_id`;
- `reminder_id`;
- `reminder_delivery_id`.

`reminder_delivery_id` is the primary semantic anchor because the user responds to a concrete sent message.

`reminder_id` and `user_id` should still be stored directly for:

- simple user-scoped queries;
- reminder-scoped history;
- easier integrity checks in callbacks;
- future reporting without always joining through deliveries.

Future implementation should enforce that the linked delivery belongs to the same user and reminder.

## Data Model Direction

Draft table:

```text
reminder_checkins
  id bigint primary key
  user_id bigint not null references users(id)
  reminder_id bigint not null references reminders(id)
  reminder_delivery_id bigint not null references reminder_deliveries(id)
  response_type text not null
  response_text text null
  created_at timestamptz not null
  updated_at timestamptz null
```

Recommended constraints:

```text
unique(reminder_delivery_id)
response_type in ('done', 'later', 'skipped')
```

Recommended indexes:

```text
index(user_id, created_at desc)
index(reminder_id, created_at desc)
```

The unique delivery constraint makes the MVP behavior one check-in per delivery. Repeat taps update the same record instead of creating duplicates.

Optional later fields:

```text
source
metadata_json
telegram_message_id
```

Do not add these until a ticket needs them.

## MVP Response Types

MVP response types:

```text
done
later
skipped
```

Meanings:

- `done` means the user acted on or acknowledged the reminder.
- `later` means the user is recording "not now" for this ping.
- `skipped` means the user intentionally declines this ping.

Do not add a `pending` check-in record in MVP. Pending is the absence of a check-in for a sent delivery.

## Later Is Not Snooze

In MVP, `later` is only a recorded response.

It must not:

- mutate `next_run_at`;
- create a one-off delayed delivery;
- pause or resume the reminder;
- override the reminder's schedule;
- create retry-like behavior.

Rationale:

- Snooze changes scheduling semantics and needs its own design.
- DIREM already has no-catch-up-storm rules; hidden snooze behavior would make delivery timing harder to reason about.
- A simple recorded `later` signal is enough to prove whether response capture is useful.

Future snooze should be a separate ticket with explicit schedule rules.

## Text Responses Are Postponed

Free-text responses are out of MVP.

Reasons:

- They require input capture rules and state management.
- They raise moderation/privacy/export questions.
- They need a clear history view before they become useful.
- They may invite AI summaries, which are explicitly out of scope for now.

The draft table keeps `response_text` nullable so a future text check-in ticket can extend the model without renaming the entity.

## Telegram UX Direction

Future delivery messages should include inline response buttons only after a successful delivery record exists.

MVP buttons:

```text
Done
Later
Skipped
```

Localization direction:

```text
ru: Готово / Позже / Пропущено
kk: Дайын / Кейін / Өткізілді
en: Done / Later / Skipped
```

The exact copy can be polished in the implementation ticket.

Callback data should be compact and safe. Recommended direction:

```text
checkin:<delivery_id>:<response_type>
```

The callback handler must:

- load the delivery;
- verify it belongs to the current Telegram user;
- verify the linked reminder is not deleted;
- upsert the check-in;
- answer stale or invalid callbacks without crashing.

## Repeat-click Behavior

MVP behavior:

- one current check-in per delivery;
- tapping the same response again is idempotent;
- tapping a different response updates the existing check-in to the new response type;
- `updated_at` changes when the response type changes;
- no duplicate check-in rows are created.

User-facing behavior:

- first tap: confirm the selected response;
- same tap again: friendly "already marked" response;
- different tap: friendly "updated" response.

This keeps the UI forgiving without adding a full edit flow.

## Bunker Interaction

Bunker-active users do not receive reminder deliveries.

Therefore:

- Bunker-suppressed reminders do not create delivery records;
- no response buttons are shown for suppressed reminders;
- no check-in records are created for suppressed reminders;
- Bunker suppression is not `skipped`;
- exiting Bunker reschedules active reminders using the existing Bunker/no-catch-up behavior, not check-ins.

If a delivery message was sent before Bunker was activated, its check-in buttons may still be tapped later. The handler should accept the response if the delivery belongs to the user and the reminder still exists. Bunker state should not retroactively invalidate an already sent delivery.

## Reminder Status Interaction

Check-ins must not mutate reminder status in MVP.

Rules:

- `done` does not pause or complete a reminder;
- `later` does not snooze a reminder;
- `skipped` does not delete or pause a reminder;
- deleted reminders should reject stale callbacks cleanly;
- paused reminders may still have old sent deliveries with valid historical check-ins.

## History Direction

History is out of scope for the first data/button implementation, but the model should support it.

Likely future views:

- recent check-ins for the current user;
- check-ins for one reminder;
- delivery + check-in timeline;
- weekly/project pulse later.

Do not implement `/history` in the data foundation ticket unless the active ticket explicitly says so.

## Implementation Ticket Split

Recommended follow-up sequence:

1. `DIREM-032-checkin-data-foundation`
   - add `ReminderCheckIn` model;
   - add Alembic migration;
   - add response-type constants;
   - add repository/service upsert/read skeleton;
   - schema and service tests.

2. `DIREM-033-checkin-buttons-mvp`
   - add inline buttons to successful worker deliveries;
   - add callback handler;
   - enforce user isolation;
   - handle stale callbacks;
   - localize button labels and confirmations.

3. `DIREM-034-checkin-history-command`
   - add user-scoped history command or hub entry;
   - show recent deliveries with check-in state;
   - keep pagination small if needed.

4. `DIREM-035-text-checkins`
   - capture optional free-text response;
   - define state flow and privacy/copy rules;
   - preserve user-authored content exactly.

5. `DIREM-036-snooze-later-scheduling`
   - design and implement real snooze separately from `later`;
   - define schedule mutation rules;
   - avoid catch-up storms and hidden retries.

## Non-goals

Do not include in the initial check-in implementation:

- migrations in this design ticket;
- Telegram callbacks in this design ticket;
- history command in the data foundation ticket;
- free-text response capture in MVP buttons;
- snooze behavior;
- analytics/dashboard;
- AI summaries;
- reminder editing;
- task manager semantics.

## Open Questions

- Should old delivery buttons expire after a fixed time?
- Should a check-in be allowed after reminder deletion for historical accuracy, or rejected for simplicity?
- Should `later` eventually offer fixed snooze choices?
- Should history show deliveries with no check-in as "no response" or hide them by default?
- Should response buttons include compact icons, plain words or both?

These questions should be answered in the relevant implementation tickets, not in D031.
