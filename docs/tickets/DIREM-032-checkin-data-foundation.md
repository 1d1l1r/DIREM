# DIREM-032 — Check-in Data Foundation

## Status
Ready for implementation

## Version target
DIREM v0.3.0 — Response Check-ins foundation

## Workstream
Backend / Domain

## Recommended branch
feature/DIREM-032-checkin-data-foundation

## Purpose

Add persistence foundation for user responses to delivered reminders.

DIREM-031 designed Response Check-ins as a separate reminder-domain concept:

```text
Reminder = recurring intention rule and schedule
Delivery = one concrete sent reminder message
Check-in = user's response to that delivery

This ticket implements only the data/model/repository/service foundation.

It must not add Telegram buttons, callbacks, worker message buttons, history screens, text capture or snooze behavior.

Source of truth

Read before implementation:

docs/CONCEPT.md
docs/ARCHITECTURE.md
docs/DECISIONS.md
docs/design/DIREM-031-response-checkins.md
docs/BACKLOG.md
docs/ROADMAP.md
docs/tickets/DIREM-032-checkin-data-foundation.md

DI-CODE reference:

.docs-local/DI-CODE/DI-CODE_CANON.md
.docs-local/DI-CODE/DI-CODE_GITHUB_WORKFLOW.md
.docs-local/DI-CODE/DI-CODE_TICKET_HANDOFF_PLAYBOOK.md
.docs-local/DI-CODE/DI-CODE_COMMIT-ATTRIBUTION.md

Important:

Follow the active ticket first.
Use DI-CODE_GITHUB_WORKFLOW.md for branch/commit/push rules.
Use DI-CODE_COMMIT-ATTRIBUTION.md for commit credits if committing.
Do not stage, commit or push .docs-local/, DI-CODE/, or docs/DI-CODE/.
Current state / dependencies

Assume these are accepted and merged into main:

DIREM-031 — Response Check-ins Design

Current behavior:

worker creates reminder_deliveries for sent/failed reminders;
delivered reminders do not yet have user response buttons;
no ReminderCheckIn model/table exists;
no check-in repository/service exists.

Accepted design:

entity name: ReminderCheckIn;
table name: reminder_checkins;
response types for MVP:
done;
later;
skipped;
later is only a recorded response, not snooze;
absence of a check-in row means no response yet;
Bunker-suppressed reminders create no delivery and therefore no check-in.
Scope
In scope

Add persistence and domain foundation for check-ins.

Need:

add ReminderCheckIn SQLAlchemy model;
add Alembic migration for reminder_checkins;
add response type constants/enums;
add repository methods for creating/updating and reading check-ins;
add service methods for recording a response to a delivery;
validate response type;
preserve user isolation;
link check-ins to:
user;
reminder;
reminder delivery;
allow one current check-in per delivery;
support repeat-click behavior by updating the existing check-in row, not creating duplicates;
preserve optional response_text column for future text check-ins;
add tests;
update CHANGELOG.
Recommended table shape

Follow existing project conventions for primary keys and timestamps.

Expected fields:

reminder_checkins
  id
  user_id NOT NULL FK users.id
  reminder_id NOT NULL FK reminders.id
  reminder_delivery_id NOT NULL FK reminder_deliveries.id
  response_type NOT NULL
  response_text NULL
  created_at NOT NULL
  updated_at NULL

Constraints:

unique(reminder_delivery_id)

Rationale:

one current check-in per delivery;
repeat taps can update the existing response;
future history/audit can be a separate table if needed.

Indexes:

user_id;
reminder_id;
reminder_delivery_id;
optionally (user_id, created_at) for future history queries.
Response types

Add domain constants for:

done
later
skipped

Do not add snooze-specific response types in this ticket.

Repository / service direction

Suggested repository methods:

ReminderCheckInRepository.get_by_delivery_id_for_user(...)
ReminderCheckInRepository.upsert_for_delivery(...)
ReminderCheckInRepository.list_recent_for_user(...)  # optional skeleton only if useful

Suggested service method:

ReminderCheckInService.record_response(...)

Behavior:

verify delivery belongs to current user;
verify response type is supported;
create check-in if absent;
update existing check-in if one already exists for this delivery;
do not mutate reminder schedule;
do not mutate next_run_at;
do not create delivery records;
do not send Telegram messages.
Out of scope

Do not implement:

worker inline check-in buttons;
Telegram callback handler;
/history;
reminder details view;
text response capture flow;
snooze;
changing next_run_at for later;
analytics;
dashboard/webhook;
AI summaries;
reminder editing;
release tag.

Future tickets:

DIREM-033 — Check-in Buttons MVP;
DIREM-034 — Check-in History Command;
DIREM-035 — Text Check-ins;
DIREM-036 — Snooze / Later Scheduling.
Technical requirements
Keep migration non-destructive.
Keep timestamps UTC-aware.
Follow existing DB/model style.
Preserve existing delivery behavior.
Preserve existing Bunker behavior.
Check-in service must not treat later as snooze.
If delivery ownership validation requires expanding delivery repository, keep it minimal and tested.
If existing schema conventions conflict with the suggested table shape, report in the plan before implementation.
Data / migration

Expected migration:

create reminder_checkins;
add FKs to users/reminders/reminder_deliveries;
add unique constraint on reminder_delivery_id;
add indexes;
downgrade drops table.

No existing data backfill required.

README update

README update is optional.

README may say only if needed:

internal check-in persistence foundation exists.

README must not claim:

users can tap check-in buttons;
/history exists;
text responses exist;
snooze exists.
CHANGELOG update

Add under [Unreleased]:

- Added internal ReminderCheckIn persistence foundation for future response check-ins.

Do not say check-in buttons are user-facing yet.

Tests

Required tests:

reminder_checkins model/table metadata exists;
migration applies cleanly;
supported response types are defined: done/later/skipped;
invalid response type is rejected;
service creates check-in for a delivery belonging to current user;
repeated response for same delivery updates existing row, not duplicate;
response_text can be null;
user cannot record check-in for another user's delivery;
check-in stores user_id, reminder_id and reminder_delivery_id;
later does not mutate reminder schedule or next_run_at;
Bunker-related behavior remains unchanged.
Verification commands
python -m pytest
python -m compileall src alembic tests
docker compose config
docker compose run --rm bot alembic upgrade head
git status
git diff
Git / GitHub expectations
Follow DI-CODE_GITHUB_WORKFLOW.md.
Use feature/DIREM-032-checkin-data-foundation.
Do not commit directly to main.
Do not create a release tag.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
Report branch, commit, changed files, checks and push state.
Acceptance checklist
 ReminderCheckIn model exists.
 reminder_checkins migration exists and applies cleanly.
 Response type constants exist.
 Repository/service foundation exists.
 One current check-in per delivery is enforced.
 Repeat response updates existing check-in.
 User isolation is enforced.
 later does not change schedule or next_run_at.
 No Telegram buttons/callbacks were added.
 No history command was added.
 No snooze behavior was added.
 CHANGELOG is truthful.
 Tests pass.
 No local DI-CODE reference docs were staged.
 No release tag was created.
Implementation guard
Implement only Check-in data foundation.
Do not add Telegram check-in buttons.
Do not add callbacks.
Do not modify worker delivery message markup.
Do not implement /history.
Do not implement text response capture.
Do not implement snooze.
Do not mutate reminder schedules or next_run_at.
Do not add dashboard/webhook/AI.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
If D031 design conflicts with implementation, stop and report.
Expected result

After this ticket:

DIREM has a persisted ReminderCheckIn domain foundation;
future check-in buttons can record responses safely;
no user-facing response feature exists yet.