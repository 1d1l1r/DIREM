# DIREM-031 — Response Check-ins Design

## Status
Ready for design

## Version target
DIREM v0.3.0 planning

## Workstream
Docs / Architecture / Product

## Recommended branch
docs/DIREM-031-response-checkins-design

## Purpose

Design Response Check-ins before implementation.

DIREM currently sends reminder messages. The next product layer is letting the user respond to a delivered reminder with a simple signal such as:

- done;
- later;
- skipped.

This should become a separate domain concept, not just temporary inline button handling.

The goal of this ticket is to define the entity, behavior, data model direction, UX, edge cases and follow-up implementation tickets.

Do not implement runtime code in this ticket.

## Source of truth

Read before implementation:

- docs/CONCEPT.md
- docs/ARCHITECTURE.md
- docs/DECISIONS.md
- docs/BACKLOG.md
- docs/ROADMAP.md
- docs/RUNTIME_SMOKE.md
- docs/tickets/DIREM-031-response-checkins-design.md

DI-CODE reference:
- `.docs-local/DI-CODE/DI-CODE_CANON.md`
- `.docs-local/DI-CODE/DI-CODE_GITHUB_WORKFLOW.md`
- `.docs-local/DI-CODE/DI-CODE_TICKET_HANDOFF_PLAYBOOK.md`
- `.docs-local/DI-CODE/DI-CODE_COMMIT-ATTRIBUTION.md`

Do not stage, commit or push `.docs-local/`, `DI-CODE/`, or `docs/DI-CODE/`.

## Current state

DIREM v0.2.0 is released.

Current implemented flow:

- user creates reminders;
- worker sends due reminders;
- reminder deliveries are recorded;
- user can list/pause/resume/delete reminders;
- Bunker can suppress delivery;
- no user response/check-in entity exists yet.

## Product direction

DIREM should evolve from:

```text
DIREM sends a reminder.

to:

DIREM sends a reminder and records how the user responded to the ping.

This should not turn DIREM into a task manager.

Recommended language:

domain entity: CheckIn or ReminderCheckIn;
avoid naming it Task / Assignment in domain code;
UI can use friendly words like “response”, “mark”, “check-in”, “reaction”.
Conceptual model

Recommended conceptual split:

Reminder = schedule/rule for recurring intention return
Delivery = one concrete sent reminder message
CheckIn = user's response to that delivery

Example:

Reminder:
  title: "Return to project"
  schedule: every 60 min

Delivery:
  sent_at: 14:00

CheckIn:
  response_type: done
  responded_at: 14:03
Scope
In scope

Design:

entity name;
relationship to reminders and deliveries;
response types;
button UX;
data model direction;
Telegram callback behavior;
repeat-click behavior;
localization direction;
follow-up implementation tickets.

Answer these design questions:

Entity naming:
ReminderCheckIn?
ReminderResponse?
CheckIn?
Relationship:
Should check-in always link to reminder_delivery_id?
Should it also duplicate reminder_id and user_id for query convenience?
Response types:
done;
later;
skipped;
maybe none / pending?
MVP behavior:
Can user respond once per delivery?
Can user change response after tapping?
What happens on repeated tap?
Does later reschedule reminder or only records reaction?
Text responses:
Should free text be in MVP?
Or postponed to later ticket?
History:
Where should check-ins be shown later?
/history?
reminder details?
weekly/project pulse later?
Worker integration:
delivered reminders should include inline response buttons;
buttons should only appear when delivery record exists;
callback data must be compact and safe.
Bunker interaction:
Bunker-suppressed reminders produce no delivery;
therefore no check-in buttons and no check-in record.
Recommended initial direction

Initial recommendation for future implementation:

Entity

Use:

ReminderCheckIn

Table:

reminder_checkins

Reason:

clearer than generic responses;
tied to reminder domain;
does not sound like task manager.
Table draft
reminder_checkins
  id
  user_id
  reminder_id
  reminder_delivery_id
  response_type
  response_text nullable
  created_at
  updated_at nullable

Optional later fields:

metadata_json
source
Response types for MVP
done
later
skipped

Meaning:

done — user acted on / acknowledged the reminder;
later — user wants to postpone mentally, but D031/D032 should not implement snooze;
skipped — user intentionally ignored/declined this ping.

Important:

In MVP, later is only a recorded response.
It must not change reminder schedule or next_run_at.
Snooze is a separate future feature.
Text responses

Out of MVP.

Future ticket:

DIREM-034 — Text Check-ins
History

Out of MVP.

Future ticket:

DIREM-033 — Check-in History Command
Out of scope

Do not implement:

migration;
model;
repository;
runtime buttons;
worker changes;
Telegram callbacks;
/history;
text response capture;
snooze behavior;
analytics;
dashboard/webhook;
AI summaries;
reminder editing;
release tag.
Deliverables

Create design doc:

docs/design/DIREM-031-response-checkins.md

Update if needed:

docs/DECISIONS.md
docs/BACKLOG.md
docs/ROADMAP.md

The design doc should include:

summary;
entity naming decision;
data model draft;
user-facing UX draft;
callback behavior;
edge cases;
localization notes;
implementation ticket split;
known limitations.
Suggested future ticket split

Recommended follow-up sequence:

DIREM-032 — Check-in Data Foundation
DIREM-033 — Check-in Buttons MVP
DIREM-034 — Check-in History Command
DIREM-035 — Text Check-ins
DIREM-036 — Snooze / Later Scheduling
Acceptance checklist
 Check-in concept is clearly separated from Reminder and Delivery.
 Entity naming is recommended.
 Data model direction is drafted.
 MVP response types are defined.
 later is explicitly not snooze in MVP.
 Text responses are scoped separately.
 History is scoped separately.
 Bunker interaction is addressed.
 Follow-up implementation tickets are proposed.
 No runtime code changed.
 No migration added.
 No release tag created.
 No local DI-CODE reference docs staged.
Verification commands
git status
git diff

If code files change, stop and report.

Implementation guard
Design only.
Do not implement check-ins.
Do not add migrations.
Do not change worker delivery.
Do not add Telegram buttons/callbacks.
Do not add history.
Do not add text response capture.
Do not implement snooze.
Do not add analytics/dashboard/AI.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
Expected result

After this ticket:

Response Check-ins are designed as a separate DIREM entity;
implementation can proceed safely in smaller tickets;
DIREM does not accidentally drift into task-manager architecture.