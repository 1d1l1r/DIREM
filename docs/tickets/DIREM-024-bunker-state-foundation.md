# DIREM-024 — Bunker State Foundation

## Status
Ready for implementation

## Version target
`DIREM v0.2.0 — Bunker Mode foundation`

## Workstream
Backend / Domain

## Recommended branch
`feature/DIREM-024-bunker-state-foundation`

## Owner / Contributors

Project Owner:
- 1D1L1R

Contributors for this ticket:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — implementation executor

## Purpose

Add the data and service foundation for future Bunker Mode.

Bunker Mode was accepted as user-level delivery suppression:
- do not rewrite individual reminder statuses;
- store whether the user is currently in Bunker;
- future worker logic will skip deliveries for users with active Bunker;
- future UI will expose Bunker controls.

This ticket adds only the persistence and service layer needed for that future behavior.

## Source of truth

Read before implementation:

- docs/CONCEPT.md
- docs/ARCHITECTURE.md
- docs/DECISIONS.md
- docs/design/DIREM-023-bunker-mode.md
- docs/BACKLOG.md
- docs/ROADMAP.md
- docs/tickets/DIREM-024-bunker-state-foundation.md

DI-CODE reference:
- `.docs-local/DI-CODE/DI-CODE_CANON.md`
- `.docs-local/DI-CODE/DI-CODE_GITHUB_WORKFLOW.md`
- `.docs-local/DI-CODE/DI-CODE_TICKET_HANDOFF_PLAYBOOK.md`
- `.docs-local/DI-CODE/DI-CODE_COMMIT-ATTRIBUTION.md`

Important:

- Follow the active ticket first.
- Use DI-CODE_GITHUB_WORKFLOW.md for branch/commit/push rules.
- Do not stage, commit or push `.docs-local/`, `DI-CODE/`, or `docs/DI-CODE/`.

## Current state / dependencies

Assume these are accepted and merged into `main`:

- DIREM-023 — Bunker Mode Design

Current behavior:

- reminders have statuses such as active, paused and deleted;
- worker sends due active reminders;
- no user-level Bunker state exists yet;
- no worker suppression exists yet;
- no Telegram Bunker UI exists yet.

## Scope

### In scope

Add Bunker state persistence and domain/service foundation.

Need:

- add user-level Bunker state to persistence;
- add Alembic migration;
- add SQLAlchemy model fields or model/table according to the accepted design;
- add repository methods for reading/updating Bunker state;
- add service methods for:
  - checking current Bunker state;
  - activating Bunker;
  - deactivating Bunker;
  - idempotent behavior if already active/inactive;
- store activation timestamp where useful;
- keep all timestamps UTC;
- do not mutate reminder statuses;
- do not recalculate `next_run_at` yet;
- add tests for repository/service behavior;
- update docs if needed;
- update CHANGELOG.

Recommended simple model direction:

Add fields to `users` unless implementation finds a strong reason for a separate table:

```text
users.bunker_active BOOLEAN NOT NULL DEFAULT false
users.bunker_activated_at TIMESTAMPTZ NULL

Expected behavior:

new users default to bunker_active = false;
activating Bunker sets bunker_active = true and bunker_activated_at = now UTC;
activating when already active is safe/idempotent;
deactivating Bunker sets bunker_active = false;
deactivating when already inactive is safe/idempotent;
reminder statuses are not changed.
Out of scope

Do not implement:

/bunker command;
menu button;
Telegram callbacks;
worker delivery suppression;
reminder next_run_at recalculation on exit;
Bunker status in /list;
Bunker runtime smoke;
Bunker notification copy;
timed Bunker;
per-reminder snooze;
dashboard/webhook;
retry/history/editing features;
release tag.

Future tickets:

D025 — Worker Suppression for Bunker Mode;
D026 — Telegram Bunker UX / Menu Integration;
D027 — Bunker Runtime Smoke & Polish.
Technical requirements
Keep model change minimal.
Keep service/repository methods testable.
Keep timestamps timezone-aware UTC.
Preserve existing user registration behavior.
Preserve existing language/timezone behavior.
Do not change reminder statuses.
Do not touch worker delivery logic in this ticket.
Do not touch Telegram menu logic in this ticket except docs/changelog if needed.
If the accepted design appears to require a separate table instead of users columns, report in the plan before implementation.
Data / model changes

Expected migration:

add bunker_active;
add bunker_activated_at.

No destructive changes.

Existing users should default to not in Bunker.

README update

README update is optional.

README may say only if needed:

Bunker state foundation exists internally.

README must not claim:

Bunker Mode is available to users;
worker suppression works;
Telegram Bunker button exists.
CHANGELOG update

Add under [Unreleased]:

- Added internal user-level Bunker state foundation for future global reminder suppression.

Do not say Bunker Mode is user-facing yet.

Tests

Required tests:

new user defaults to Bunker inactive;
activate Bunker sets active state and activation timestamp;
activating twice is safe;
deactivate Bunker clears active state;
deactivating twice is safe;
existing timezone/language user behavior still works;
reminder statuses are not modified by Bunker state service.
Verification commands
python -m pytest
python -m compileall src alembic tests
docker compose config
docker compose run --rm bot alembic upgrade head
git status
git diff
Git / GitHub expectations
Follow DI-CODE_GITHUB_WORKFLOW.md.
Use feature/DIREM-024-bunker-state-foundation.
Do not commit directly to main.
Do not create a release tag.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
Report branch, commit, changed files, checks and push state.
Acceptance checklist
 Bunker state persistence exists.
 Migration is added and applies cleanly.
 Existing users default to Bunker inactive.
 Repository/service foundation exists.
 Activate/deactivate behavior is idempotent.
 Reminder statuses are not mutated.
 Worker behavior is unchanged.
 Telegram UI is unchanged.
 CHANGELOG is truthful.
 Tests pass.
 No local DI-CODE reference docs were staged.
 No release tag was created.
Implementation guard
Implement only Bunker state foundation.
Do not implement Telegram Bunker UI.
Do not implement worker suppression.
Do not mutate reminder statuses.
Do not recalculate next_run_at.
Do not implement timed Bunker.
Do not implement delivery history/retries/editing.
Do not add dashboard/webhook/AI/web UI.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
If data model direction conflicts with D023 design, stop and report.
Expected result summary

After this ticket:

DIREM can persist whether a user is in Bunker;
service/repository methods exist for future Bunker implementation;
worker/UI behavior remains unchanged until follow-up tickets.