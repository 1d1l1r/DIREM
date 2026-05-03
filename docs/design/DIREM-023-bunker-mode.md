# DIREM-023 - Bunker Mode Design

## Status

Design proposal for future implementation. Bunker Mode is not implemented.

## Purpose

Bunker Mode is a user-level global silence mode for DIREM. It lets a user temporarily stop reminder delivery without losing the previous state of individual reminders.

The design goal is simple:

- one user can enter Bunker;
- worker stops sending that user's reminders;
- reminders are not spammed after exit;
- reminders that were paused before Bunker stay paused;
- deleted reminders stay deleted;
- implementation remains Telegram-first and small.

## Core Behavior

Bunker Mode is per user.

When Bunker is active:

- worker must not send reminders for that user;
- active reminders remain logically active in their own records;
- paused reminders remain paused;
- deleted reminders remain deleted;
- reminder creation remains allowed;
- newly created reminders can be active, but delivery is suppressed until Bunker exits;
- manual reminder controls still work unless a future UX ticket explicitly disables them.

When Bunker is inactive:

- active reminders can be delivered normally;
- paused reminders are skipped;
- deleted reminders are skipped.

## Activation

Activation should require confirmation.

Activation should:

- set user-level Bunker state to active;
- store `bunker_started_at`;
- leave reminder statuses unchanged;
- show clear Telegram confirmation.

Activation should not:

- rewrite every active reminder to paused;
- create delivery records;
- recalculate `next_run_at`;
- delete or disable reminders.

Recommended Russian copy direction:

```text
Бункер включён.

DIREM пока не будет присылать напоминания.
Индивидуальные статусы напоминаний сохранены.
```

Kazakh copy direction:

```text
Бункер қосылды.

DIREM әзірге еске салуларды жібермейді.
Еске салулардың жеке күйлері сақталады.
```

English copy direction:

```text
Bunker is on.

DIREM will not send reminders for now.
Individual reminder statuses are preserved.
```

## Deactivation

Deactivation should require confirmation.

Deactivation should:

- set user-level Bunker state to inactive;
- store `bunker_ended_at` or clear active state while keeping history;
- recalculate `next_run_at` for reminders that are active at the moment of exit;
- leave paused reminders paused;
- leave deleted reminders deleted;
- avoid catch-up storms.

Deactivation should not:

- send missed reminders immediately;
- replay missed deliveries;
- change paused reminders to active unless the user manually resumed them before exit;
- create delivery records for skipped Bunker time.

Recommended Russian copy direction:

```text
Бункер выключен.

Активные напоминания продолжат работу с нового времени.
Пропущенные напоминания не будут отправлены пачкой.
```

Kazakh copy direction:

```text
Бункер өшірілді.

Белсенді еске салулар жаңа уақыттан жалғасады.
Өтіп кеткен еске салулар топ болып жіберілмейді.
```

English copy direction:

```text
Bunker is off.

Active reminders will continue from a fresh next run.
Missed reminders will not be sent in a batch.
```

## Reminder State Rules

### Active Reminders

Active reminders stay `active` while Bunker is on.

Worker suppression comes from user-level Bunker state, not from rewriting reminder status.

On Bunker exit:

- recalculate `next_run_at` for active reminders from `now`;
- use the user's timezone;
- use existing schedule calculation functions;
- apply no-catch-up-storm behavior.

### Paused Reminders

Paused reminders stay `paused`.

Bunker activation does not snapshot and later restore them, because their status never changes.

On Bunker exit:

- paused reminders remain paused;
- `next_run_at` should not be recalculated unless a future implementation already recalculates on resume.

### Deleted Reminders

Deleted reminders stay deleted.

Worker must already skip deleted reminders. Bunker does not change that.

### Reminders Created During Bunker

Reminder creation remains allowed.

New reminders created during Bunker should:

- be stored with the selected status from the existing creation flow, normally `active`;
- calculate and store `next_run_at` normally;
- not be delivered until Bunker is off;
- have `next_run_at` recalculated on Bunker exit if they are active.

Rationale:

- this keeps `/new` usable;
- user can prepare reminders while offline/silent;
- worker has one global suppression check;
- no special created-during-Bunker status is needed.

## Snapshot and Restore Semantics

Recommended direction: no per-reminder status snapshot for MVP Bunker.

Because Bunker does not rewrite reminder statuses, restoration is simply:

- user Bunker state becomes inactive;
- active reminders remain active;
- paused reminders remain paused;
- deleted reminders remain deleted;
- active reminders get fresh future `next_run_at`.

If a future design chooses to rewrite statuses during Bunker, then a snapshot table would be needed. That is not recommended for the first implementation.

## next_run_at After Exit

On Bunker exit, active reminders should be recalculated as if the user is resuming from downtime.

Rules:

- use current UTC time as `now`;
- use user timezone;
- for interval reminders, next run is `now + interval`, adjusted for active window;
- for daily reminders, next future local daily time is selected;
- active windows are respected;
- no catch-up storm;
- no immediate batch delivery of missed reminders.

If active window is currently closed:

- schedule the next valid time inside the window;
- do not send immediately.

If schedule config is invalid:

- leave reminder active but log/report implementation-level warning;
- future implementation may surface a safe user-facing message in `/list` or a diagnostics view.

## Worker Behavior

Worker must check Bunker state before delivery.

Recommended order:

1. Find due active reminders as today.
2. Join or load user state.
3. If user's Bunker is active, skip delivery.
4. Do not create delivery records for Bunker-skipped reminders in MVP.
5. Do not advance `next_run_at` while Bunker is active.
6. On Bunker exit, bot/service recalculates active reminders once.

Rationale:

- worker behavior remains easy to reason about;
- skipped Bunker time is not treated as send failure;
- delivery history stays honest;
- no missed-message storm.

Implementation note:

If worker repeatedly finds the same due reminders while Bunker is active, this is acceptable for MVP if batch size is small. If logs become noisy, implementation can filter out Bunker users in the due query.

## Telegram UX

Future UX entry point:

- main menu may add Bunker button;
- command may be `/bunker`;
- Bunker screen shows current state and actions.

Suggested states:

```text
Bunker off
Bunker on
Turn Bunker on
Turn Bunker off
Confirm
Cancel
Back
```

Activation confirmation should explain:

- reminders will be silent;
- individual statuses are preserved;
- new reminders can still be created.

Deactivation confirmation should explain:

- active reminders resume from a fresh next run;
- missed reminders are not sent in a batch.

## Data Model Direction

Recommended minimal model:

Add user-level fields, either on `users` or in a dedicated user settings/state table:

```text
users.bunker_active boolean not null default false
users.bunker_started_at timestamptz nullable
users.bunker_updated_at timestamptz nullable
```

Alternative dedicated table:

```text
user_modes
- user_id
- bunker_active
- bunker_started_at
- bunker_updated_at
```

Recommendation:

- use `users` fields for the first implementation unless the project wants a broader user settings table;
- avoid JSON snapshot for MVP;
- avoid per-reminder snapshot table for MVP.

## Migration Implications

Bunker implementation requires a migration.

Expected Alembic migration:

- add `bunker_active`;
- add `bunker_started_at`;
- add `bunker_updated_at`;
- backfill existing users to `bunker_active = false`;
- add index only if worker query needs it after implementation profiling.

No migration is part of this design ticket.

## Future Tests

Implementation should test:

- activate Bunker for one user;
- deactivate Bunker for one user;
- Bunker is user-isolated;
- worker skips active reminders for Bunker user;
- worker still sends reminders for non-Bunker user;
- paused reminders remain paused after exit;
- deleted reminders remain deleted after exit;
- reminders created during Bunker are suppressed;
- active reminders get recalculated `next_run_at` on exit;
- no catch-up storm after exit;
- invalid/stale Bunker callbacks do not crash;
- ru/kk/en copy exists.

## Follow-up Implementation Tickets

Recommended split:

1. `DIREM-024-bunker-data-model`
   - add user-level Bunker fields;
   - migration;
   - repository/service methods;
   - schema tests.

2. `DIREM-025-bunker-domain-service`
   - activate/deactivate service;
   - active reminder recalculation on exit;
   - no-catch-up behavior tests.

3. `DIREM-026-bunker-worker-suppression`
   - worker skip check;
   - user isolation tests;
   - no delivery records for Bunker skips.

4. `DIREM-027-bunker-telegram-ux`
   - `/bunker` command or menu hub;
   - confirmation/cancel callbacks;
   - localized copy;
   - runtime smoke update.

## Non-goals

Do not include in first Bunker implementation:

- per-reminder snooze;
- timed Bunker until a date/time;
- global system-wide pause;
- status snapshot/restore table unless requirements change;
- delivery records for Bunker skips;
- analytics/dashboard;
- automatic detection of user availability.

## Open Questions

- Should Bunker have an optional duration later?
- Should `/list` visually mark that Bunker is active?
- Should reminder creation while Bunker is active show a small warning?
- Should owner diagnostics show how many reminders are suppressed?

These are intentionally parked for later tickets.
