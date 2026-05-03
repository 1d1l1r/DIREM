# DIREM-026 — Telegram Bunker UX and Exit Reschedule

## Status
Ready for implementation

## Version target
`DIREM v0.2.0 — Bunker Mode`

## Workstream
General

## Recommended branch
`feature/DIREM-026-telegram-bunker-ux`

## Owner / Contributors

Project Owner:
- 1D1L1R

Contributors for this ticket:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — implementation executor

## Purpose

Expose Bunker Mode to users through Telegram.

DIREM-024 added user-level Bunker state.
DIREM-025 made the worker suppress reminders for users with active Bunker state.

DIREM-026 adds the Telegram UX for toggling Bunker Mode and safely recalculates active reminders when Bunker is turned off.

Bunker Mode is user-level delivery suppression:
- it does not rewrite reminder statuses;
- active reminders remain active but are not delivered while Bunker is on;
- paused reminders remain paused;
- deleted reminders remain deleted.

## Source of truth

Read before implementation:

- docs/CONCEPT.md
- docs/ARCHITECTURE.md
- docs/DECISIONS.md
- docs/design/DIREM-023-bunker-mode.md
- docs/BACKLOG.md
- docs/ROADMAP.md
- docs/RUNTIME_SMOKE.md
- docs/tickets/DIREM-026-telegram-bunker-ux.md

DI-CODE reference:
- `.docs-local/DI-CODE/DI-CODE_CANON.md`
- `.docs-local/DI-CODE/DI-CODE_GITHUB_WORKFLOW.md`
- `.docs-local/DI-CODE/DI-CODE_TICKET_HANDOFF_PLAYBOOK.md`
- `.docs-local/DI-CODE/DI-CODE_COMMIT-ATTRIBUTION.md`

Important:

- Follow the active ticket first.
- Use DI-CODE_GITHUB_WORKFLOW.md for branch/commit/push rules.
- Use DI-CODE_COMMIT-ATTRIBUTION.md for commit credits if committing.
- Do not stage, commit or push `.docs-local/`, `DI-CODE/`, or `docs/DI-CODE/`.

## Current state / dependencies

Assume these are accepted and merged into `main`:

- DIREM-023 — Bunker Mode Design
- DIREM-024 — Bunker State Foundation
- DIREM-025 — Worker Suppression for Bunker Mode

Current behavior:

- users have `bunker_active` and `bunker_activated_at`;
- worker skips reminders for Bunker-active users;
- suppressed reminders are not sent;
- suppressed reminders do not create delivery records;
- suppressed reminders do not advance `next_run_at`;
- no Telegram UI exists for Bunker yet.

## Scope

### In scope

Add Telegram Bunker UX and safe Bunker exit rescheduling.

Need:

- add `/bunker` command;
- add `/bunker` to Telegram command menu;
- add Bunker entry to main menu screen;
- show Bunker state on main menu:
  - inactive;
  - active;
- add localized Bunker status screen;
- add inline buttons:
  - activate Bunker;
  - deactivate Bunker;
  - back/home;
- activating Bunker:
  - sets user Bunker active through existing service;
  - does not mutate reminder statuses;
  - does not change `next_run_at`;
  - confirms activation to user;
- deactivating Bunker:
  - sets user Bunker inactive through existing service;
  - recalculates `next_run_at` for active, non-deleted reminders;
  - does not touch paused reminders;
  - does not touch deleted reminders;
  - does not create delivery records;
  - does not send reminder messages;
  - confirms deactivation to user;
- use existing schedule calculation/no-catch-up behavior where practical;
- localize all user-facing Bunker copy for:
  - ru;
  - kk;
  - en;
- update `/help` if needed;
- update README;
- update RUNTIME_SMOKE;
- update CHANGELOG;
- add tests.

### Suggested main menu button labels

Russian:

```text
Бункер выключен ⚪
Бункер активен 🟢

Main screen can show one Bunker button below top-level navigation or alongside it.

Do not remove existing List / Settings / Help hubs.

Suggested Bunker screen copy

Inactive:

Бункер выключен.

В этом режиме DIREM работает как обычно.

Active:

Бункер активен.

DIREM временно не отправляет напоминания.
Ваши напоминания не удалены и не переведены в паузу.

Activation confirmation:

Бункер активирован.

DIREM временно остановит доставку напоминаний.

Deactivation confirmation:

Бункер выключен.

Активные напоминания перепланированы без догоняющей рассылки.
Out of scope

Do not implement:

timed Bunker;
per-reminder snooze;
Bunker history;
delivery history command;
retry scheduler;
reminder editing;
dashboard/webhook;
AI features;
web UI;
new delivery status;
snapshot table;
bulk reminder status rewrite;
migrations unless absolutely required.
Technical requirements
Reuse BunkerService from D024.
Reuse worker suppression behavior from D025.
Do not mutate reminder statuses.
Do not create delivery records during Bunker toggle.
Do not send reminders during Bunker toggle.
On Bunker deactivate, recalculate next_run_at only for active, non-deleted reminders.
Use user timezone for recalculation.
Use existing schedule helpers from the schedule domain where practical.
Avoid catch-up storm after Bunker exit.
Keep handlers thin.
Callback data must be short and safe.
Stale/invalid callbacks must not crash the bot.
No migration expected.
Data / model changes

Expected:

No data/model changes.
No migration.

If implementation appears to require data/model changes, stop and report first.

User behavior

User sends /bunker:

sees current Bunker state;
can activate or deactivate;
can return home.

User taps Bunker from main menu:

sees the same Bunker screen.

While Bunker is active:

worker does not deliver reminders;
reminders remain visible and retain their statuses;
paused reminders remain paused.

When user deactivates Bunker:

Bunker becomes inactive;
active reminders get fresh future next_run_at;
paused reminders remain paused;
no old backlog is sent.
README update

README may say:

Bunker Mode is available through /bunker and main menu;
Bunker temporarily suppresses delivery for the current user;
Bunker does not delete reminders or rewrite reminder statuses;
deactivation reschedules active reminders to avoid catch-up storm.

README must not claim:

timed Bunker;
per-reminder snooze;
Bunker history;
delivery history;
retry scheduler;
dashboard/webhook;
AI features.
CHANGELOG update

Add under [Unreleased]:

- Added Telegram Bunker Mode UX for temporarily suppressing reminder delivery.
- Added Bunker deactivation rescheduling to avoid catch-up reminder storms.
Tests

Required tests:

/bunker renders inactive state;
/bunker renders active state;
main menu includes localized Bunker button/state;
activating Bunker sets user state active;
activating Bunker does not mutate reminder statuses;
deactivating Bunker sets user state inactive;
deactivating Bunker recalculates next_run_at for active reminders;
deactivating Bunker does not recalculate paused reminders;
deactivating Bunker does not touch deleted reminders;
deactivating Bunker does not create delivery records;
Bunker copy/buttons are localized for ru/kk/en;
stale/invalid callback does not crash;
existing main menu/list/settings/help flows still pass.
Manual smoke
/start
tap Bunker
tap Activate Bunker
/start
verify Bunker shows active
create or keep an active due reminder
wait long enough that it would normally be due
verify worker does not send while Bunker is active
/bunker
tap Deactivate Bunker
verify active reminders are rescheduled
verify no catch-up storm happens
/start
verify Bunker shows inactive

Also check:

/language → Қазақша → /bunker
/language → English → /bunker
/language → Русский → /bunker

Expected:

Bunker UI is localized;
worker suppression works through real toggle;
reminder statuses are preserved;
Bunker exit does not trigger old reminder backlog.
Acceptance checklist
 /bunker command exists.
 /bunker is in command menu.
 Main menu exposes Bunker entry/state.
 Bunker status screen exists.
 Activate works.
 Deactivate works.
 Worker suppression works through user toggle.
 Deactivation recalculates active reminders.
 Paused reminders are not resumed.
 Deleted reminders are not touched.
 Reminder statuses are not rewritten.
 No delivery records are created by toggle actions.
 No catch-up storm after Bunker exit.
 ru/kk/en copy exists.
 README truth is preserved.
 CHANGELOG truth is preserved.
 RUNTIME_SMOKE is updated.
 Tests pass.
 No local DI-CODE reference docs were staged.
 No release tag was created.
Verification commands
python -m pytest
python -m compileall src alembic tests
docker compose config
git status
git diff
Git / GitHub expectations
Follow DI-CODE_GITHUB_WORKFLOW.md.
Use feature/DIREM-026-telegram-bunker-ux.
Do not commit directly to main.
Do not create a release tag.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
Report branch, commit, changed files, checks and push state.
Implementation guard
Implement only Telegram Bunker UX and exit rescheduling.
Do not implement timed Bunker.
Do not implement per-reminder snooze.
Do not implement Bunker history.
Do not implement delivery history/retries/editing.
Do not add dashboard/webhook/AI/web UI.
Do not rewrite reminder statuses.
Do not add migrations unless implementation cannot meet acceptance without one; if so, stop and report first.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
If implementation conflicts with D023/D024/D025, stop and report.
Expected result summary

After this ticket:

users can toggle Bunker Mode from Telegram;
worker suppression becomes user-accessible;
Bunker exit safely reschedules active reminders;
Bunker becomes a complete basic user-facing feature.