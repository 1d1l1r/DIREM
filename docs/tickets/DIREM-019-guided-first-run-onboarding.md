# DIREM-019 — Guided First-run Onboarding

## Status
Implemented

## Version target
`DIREM v0.1.1 — UX polish`

## Workstream
General

## Recommended branch
`feature/DIREM-019-guided-first-run-onboarding`

## Owner / Contributors

Project Owner:
- 1D1L1R

Contributors for this ticket:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — implementation executor

## Purpose

Improve the first-run experience after `/start`.

DIREM v0.1.0 is released and functional, but a new user still needs to understand the shortest useful path:

1. choose language;
2. set timezone;
3. create first reminder;
4. understand list/control basics.

This ticket adds lightweight guided onboarding without adding new reminder product features.

## Source of truth

Read before implementation:

- docs/CONCEPT.md
- docs/PRODUCT_SCOPE.md
- docs/ARCHITECTURE.md
- docs/VERSIONING.md
- docs/COAUTHORS.md
- docs/ROADMAP.md
- docs/DECISIONS.md
- docs/BACKLOG.md
- docs/RUNTIME_SMOKE.md
- docs/tickets/DIREM-019-guided-first-run-onboarding.md

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

Released:

- `direm-v0.1.0` — Core MVP

Post-release planning accepted:

- DIREM-018 — post-release backlog planning

Current behavior:

- `/start` creates or updates user;
- `/language` selects ru/kk/en;
- `/timezone` stores IANA timezone;
- `/new` creates reminder;
- `/list`, `/pause`, `/resume`, `/delete` manage reminders;
- `/help` is grouped and localized;
- Help/Cancel reply keyboard exists;
- inline buttons exist for language and reminder control.

## Scope

### In scope

Add lightweight onboarding after `/start`.

Need:

- detect first-run/new-user case where practical;
- after `/start`, show short localized onboarding text;
- explain DIREM in one or two short lines;
- show suggested next actions with inline buttons or reply buttons:
  - choose language;
  - set timezone;
  - create first reminder;
  - open help;
- preserve existing `/start` behavior for repeated starts;
- repeated `/start` should not force a full tutorial every time;
- if user already exists, show a shorter welcome-back message or normal start response;
- localize onboarding text for:
  - ru;
  - kk;
  - en;
- do not translate user-authored reminder content;
- keep onboarding lightweight;
- update `/help` only if needed;
- update README if needed;
- update RUNTIME_SMOKE;
- update CHANGELOG;
- add tests.

### Out of scope

Do not implement:

- heavy onboarding state machine unless strictly necessary;
- mandatory tutorial;
- progress tracking with complex states;
- new reminder features;
- timezone picker UX;
- reminder editing;
- delivery history;
- retries;
- dashboard/webhook;
- AI features;
- web UI;
- migrations unless absolutely required and justified.

Future/parked work:

- DIREM-020 — Timezone Picker UX;
- DIREM-021 — Language and Copy Polish;
- DIREM-022 — Empty States and Confirmation Polish.

## Technical requirements

- Prefer reusing existing user persistence and handler/service structure.
- Keep handlers thin.
- Reuse existing i18n catalog/helper.
- Reuse existing `/language`, `/timezone`, `/new`, `/help` commands rather than duplicating flows.
- If inline buttons are used, callback data must be short and safe.
- If no DB change is needed, do not add migration.

## User behavior

New user after `/start` should see something like:

```text
DIREM помогает возвращаться к намерениям во времени.

Быстрый старт:
1. Выбери язык.
2. Укажи часовой пояс.
3. Создай первое напоминание.

With actions:

[Выбрать язык]
[Указать часовой пояс]
[Создать напоминание]
[Помощь]

Existing user after /start should not be forced through onboarding again.

Localization / copy behavior

Supported languages:

ru;
kk;
en.

Kazakh text should be simple and natural interface Kazakh.

Reminder title/message text must remain exactly as user wrote it.

Data / model changes

Prefer:

No data/model changes.

If implementation proves a small persisted onboarding flag is necessary, stop and report before adding migration.

README update

README may say:

/start provides lightweight first-run guidance;
onboarding points users to /language, /timezone, /new, and /help.

README must not claim:

mandatory tutorial;
progress tracking;
AI assistant onboarding;
timezone auto-detection.
CHANGELOG update

CHANGELOG should say:

- Added lightweight localized first-run onboarding after `/start`.

If no README change is needed, do not force it.

Tests

Required tests:

new user receives onboarding path;
existing user is not forced through full onboarding;
onboarding text/actions are localized for ru/kk/en;
onboarding actions point to existing flows;
/start still preserves existing timezone and language;
no reminder flow regression.
Manual smoke
/start as new user
/language
/timezone
/new
/start as existing user

Expected:

new user gets short guidance;
existing user gets non-intrusive start response;
language/timezone/new flows still work;
Help/Cancel reply keyboard still works.
Acceptance checklist
 /start gives lightweight first-run guidance for new users.
 Existing users are not forced through full onboarding.
 ru/kk/en onboarding text exists.
 Existing /language, /timezone, /new, /help flows are reused.
 No heavy tutorial or new product feature was added.
 README truth is preserved.
 CHANGELOG truth is preserved.
 RUNTIME_SMOKE is updated if needed.
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
Use feature/DIREM-019-guided-first-run-onboarding.
Do not commit directly to main.
Do not create a release tag.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
Report branch, commit, changed files, checks and push state.
Implementation guard
Implement only this onboarding ticket.
Do not implement timezone picker.
Do not implement reminder editing.
Do not implement delivery history.
Do not implement retries.
Do not add dashboard/webhook/AI/web UI.
Do not add migrations unless implementation cannot meet acceptance without one; if so, stop and report first.
Preserve versioning and credits metadata.
Update README/CHANGELOG only with truthful current-state wording.
If docs/ticket/code conflict, stop and report the conflict.
Expected result summary

After this ticket:

new users get a clearer first-run path;
existing users are not bothered by a heavy tutorial;
DIREM remains Telegram-first and lightweight;
future timezone picker remains a separate ticket.
