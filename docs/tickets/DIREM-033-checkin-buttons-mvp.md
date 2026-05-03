# DIREM-033 — Check-in Buttons MVP

## Status
Ready for implementation

## Version target
DIREM v0.3.0 — Response Check-ins MVP

## Workstream
Worker / Telegram UX

## Recommended branch
feature/DIREM-033-checkin-buttons-mvp

## Purpose

Add inline response buttons to delivered reminder messages.

DIREM-032 added the internal ReminderCheckIn persistence foundation. This ticket makes check-ins user-facing for delivered reminders.

When worker successfully sends a reminder, the Telegram message should include inline buttons:

- Done
- Later
- Skipped

Tapping a button records a `ReminderCheckIn` for the corresponding delivery.

`later` remains only a recorded response. It must not snooze or change reminder scheduling.

## Source of truth

Read before implementation:

- docs/CONCEPT.md
- docs/ARCHITECTURE.md
- docs/DECISIONS.md
- docs/design/DIREM-031-response-checkins.md
- docs/BACKLOG.md
- docs/ROADMAP.md
- docs/tickets/DIREM-033-checkin-buttons-mvp.md

DI-CODE reference:
- `.docs-local/DI-CODE/DI-CODE_CANON.md`
- `.docs-local/DI-CODE/DI-CODE_GITHUB_WORKFLOW.md`
- `.docs-local/DI-CODE/DI-CODE_TICKET_HANDOFF_PLAYBOOK.md`
- `.docs-local/DI-CODE/DI-CODE_COMMIT-ATTRIBUTION.md`

Do not stage, commit or push `.docs-local/`, `DI-CODE/`, or `docs/DI-CODE/`.

## Current state / dependencies

Assume these are accepted and merged into `main`:

- D031 — Response Check-ins Design
- D032 — Check-in Data Foundation

Current behavior:

- worker sends due reminders;
- successful sends create `reminder_deliveries`;
- ReminderCheckIn model/repository/service exists;
- no user-facing check-in buttons exist yet.

Accepted design:

- response types:
  - `done`;
  - `later`;
  - `skipped`;
- one current check-in per delivery;
- repeated taps update the existing check-in;
- `later` is not snooze;
- Bunker-suppressed reminders create no delivery and no check-in.

## Scope

### In scope

Add check-in buttons to successfully delivered reminders.

Need:

- add inline keyboard to successful worker-sent reminder messages;
- buttons:
  - Done;
  - Later;
  - Skipped;
- callback handler for check-in buttons;
- callback must record response through existing `ReminderCheckInService`;
- validate current Telegram user owns the delivery;
- repeat taps should update existing check-in;
- answer callback with localized confirmation;
- optionally edit the inline keyboard or message markup to reflect selected response if simple;
- localize button labels and confirmation copy for:
  - ru;
  - kk;
  - en;
- update README/RUNTIME_SMOKE/CHANGELOG;
- add tests.

### Suggested RU labels

Buttons:

```text
[Сделано] [Позже] [Пропустить]

Confirmations:

Отмечено: сделано.
Отмечено: позже.
Отмечено: пропущено.
Suggested EN labels
[Done] [Later] [Skipped]
Suggested KK labels

Keep simple interface Kazakh.

Out of scope

Do not implement:

text response capture;
/history;
analytics;
AI summaries;
snooze;
changing reminder next_run_at for later;
reminder editing;
delivery retry changes;
dashboard/webhook;
new migrations unless absolutely required.
Technical requirements
Callback data must be compact and safe.
Callback must include enough information to identify delivery and response type.
Do not expose raw internal IDs in user-visible text.
User isolation must be enforced server-side.
Do not trust Telegram callback data alone.
Use existing check-in service for persistence.
Bunker-suppressed reminders have no delivery/check-in buttons because they are not sent.
Failed deliveries should not create check-in buttons.
later must not mutate reminder schedule or next_run_at.
Callback behavior

When user taps a check-in button:

validate callback data;
load delivery for current user;
record response;
return localized confirmation;
stale/invalid/foreign callback should not crash;
if delivery is not found or not owned by user, show safe localized error.

Repeat click:

update existing check-in response;
confirmation should reflect latest chosen response.
README update

README may say:

delivered reminders include Done/Later/Skipped check-in buttons;
check-ins are recorded per delivery.

README must not claim:

/history;
text responses;
snooze;
analytics;
AI summaries.
CHANGELOG update

Add under [Unreleased]:

- Added Done/Later/Skipped check-in buttons to delivered reminders.
Tests

Required tests:

worker sends successful reminder with check-in inline buttons;
sent delivery ID is associated with callback data safely;
tapping Done records done;
tapping Later records later without changing next_run_at;
tapping Skipped records skipped;
repeat tap updates existing check-in row;
foreign user cannot record response for another user's delivery;
invalid/stale callback does not crash;
failed delivery does not create check-in buttons;
Bunker-suppressed reminder has no delivery and no buttons;
ru/kk/en button labels and confirmations exist.
Manual smoke
Create a near-due reminder.
Wait for worker delivery.
Tap Done.
Verify confirmation.
Tap Later on the same delivery if still visible.
Verify response updates, not duplicates.
Create another delivery.
Tap Skipped.
Verify no schedule mutation from Later.

Expected:

delivered reminders show check-in buttons;
taps record responses;
Later does not snooze;
no history/text response features are shown.
Verification commands
python -m pytest
python -m compileall src alembic tests
docker compose config
docker compose run --rm bot alembic upgrade head
git status
git diff
Acceptance checklist
 Delivered reminders include Done/Later/Skipped buttons.
 Check-in callbacks record responses.
 Repeat taps update existing response.
 User isolation is enforced.
 Later does not change schedule or next_run_at.
 Failed deliveries do not expose check-in buttons.
 Bunker-suppressed reminders do not create buttons.
 ru/kk/en copy exists.
 README truth is preserved.
 CHANGELOG truth is preserved.
 Tests pass.
 No local DI-CODE reference docs were staged.
 No release tag was created.
Implementation guard
Implement only Check-in Buttons MVP.
Do not implement /history.
Do not implement text response capture.
Do not implement snooze.
Do not mutate reminder schedules or next_run_at for later.
Do not implement analytics/dashboard/AI.
Do not change retry behavior.
Do not add migrations unless absolutely required.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
Expected result

After this ticket:

delivered reminders can receive simple Done/Later/Skipped responses;
check-ins are persisted through the D032 foundation;
history/text/snooze remain separate future tickets.