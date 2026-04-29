# DIREM-017 — v0.1.0 Release Pass

## Status
Implemented

## Version target
`DIREM v0.1.0 — Core MVP`

## Workstream
Docs / Release

## Recommended branch
`release/direm-v0.1.0`

## Owner / Contributors

Project Owner:
- 1D1L1R

Contributors for this ticket:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — release executor

## Purpose

Prepare and verify DIREM v0.1.0 Core MVP release.

This ticket must not add new product features. It only verifies the current MVP state, finalizes release documentation, prepares release notes, and confirms that the repository is safe to tag.

After this ticket, DIREM should be ready for the `direm-v0.1.0` release tag.

## Source of truth

Read before implementation:

- docs/CONCEPT.md
- docs/PRODUCT_SCOPE.md
- docs/ARCHITECTURE.md
- docs/VERSIONING.md
- docs/COAUTHORS.md
- docs/ROADMAP.md
- docs/DECISIONS.md
- docs/RUNTIME_SMOKE.md
- docs/tickets/DIREM-017-v0.1.0-release-pass.md

DI-CODE reference, local-only if available:

- .docs-local/DI-CODE/DI-CODE_CANON.md
- .docs-local/DI-CODE/DI-CODE_GITHUB_WORKFLOW.md
- .docs-local/DI-CODE/DI-CODE_TICKET_HANDOFF_PLAYBOOK.md
- .docs-local/DI-CODE/DI-CODE_COMMIT-ATTRIBUTION.md

Important:

- Follow the active ticket first.
- Use DI-CODE_GITHUB_WORKFLOW.md for branch/commit/push rules.
- Use DI-CODE_COMMIT-ATTRIBUTION.md for commit credits if committing.
- Do not stage, commit or push `.docs-local/`, `DI-CODE/`, or `docs/DI-CODE/`.

## Current state / dependencies

Assume these tickets are accepted and merged into `main`:

- DIREM-001 — project skeleton
- DIREM-002 — domain schema
- DIREM-003 — schedule calculation domain
- DIREM-004 — user registration + `/timezone`
- DIREM-005 — `/new`
- DIREM-006 — `/list`
- DIREM-007 — `/pause` and `/resume`
- DIREM-008 — `/delete`
- DIREM-009 — worker delivery MVP
- DIREM-010 — runtime smoke / release readiness
- DIREM-011 — `/new` callback session injection fix
- DIREM-012 — control active-window rendering fix
- DIREM-013 — Telegram command menu and `/cancel`
- DIREM-014 — inline reminder control buttons
- DIREM-015 — language selection + ru/kk/en i18n foundation
- DIREM-016 — pre-release Telegram UX polish

Current MVP behavior:

- `/start`
- `/help`
- `/language`
- `/timezone`
- `/new`
- `/list`
- `/pause`
- `/resume`
- `/delete`
- `/version`
- `/credits`
- `/cancel`
- worker delivery MVP
- Russian / Kazakh / English interface language
- localized Help/Cancel reply keyboard
- inline control buttons for reminder control

Still not implemented:

- retry scheduler
- AI translation
- delivery history command
- delivery dashboard
- webhook mode
- reminder editing
- web UI

## Scope

### In scope

- verify `main` includes all accepted D001–D016 work;
- verify PR #3 / final help-copy micro-patch is merged before release branch starts;
- create release branch from updated `main`;
- run final automated checks;
- verify migrations apply cleanly;
- verify README truth;
- verify CHANGELOG truth;
- replace `[0.1.0] - Unreleased` with release date if owner approves finalization;
- prepare release notes for `direm-v0.1.0`;
- verify `.gitignore` excludes secrets and local DI-CODE reference docs;
- verify `.env` is not tracked;
- verify no local DI-CODE docs are staged;
- verify runtime smoke checklist matches current behavior;
- report whether `direm-v0.1.0` tag is safe to create.

### Out of scope

Do not implement:

- new reminder features;
- guided onboarding;
- timezone picker by country/continent/GMT;
- reminder editing;
- retry scheduler;
- delivery history command;
- dashboard;
- webhook mode;
- Redis/Celery;
- AI features;
- web UI;
- broad copy rewrite;
- new runtime architecture;
- release tag unless owner explicitly approves after release pass.

## Technical requirements

- no product behavior changes unless a release-blocking bug is found;
- release-blocking bugs must be reported before fixing unless trivial docs/check typo;
- if a real bug is found, recommend hotfix ticket instead of hiding it inside release pass;
- do not rotate or expose tokens;
- do not commit `.env`;
- do not commit `.docs-local/`, `DI-CODE/`, or `docs/DI-CODE/`.

## README update

README may claim:

- DIREM v0.1.0 Core MVP includes current Telegram commands;
- worker delivery is basic MVP;
- ru/kk/en language selection exists;
- user-authored reminder content is not auto-translated;
- retries/history/dashboard/webhook are not implemented.

README must not claim:

- production-grade delivery;
- retries;
- dashboard;
- delivery history;
- webhook mode;
- AI translation;
- reminder editing;
- timezone auto-detection.

## CHANGELOG update

CHANGELOG should finalize v0.1.0 if release pass is accepted.

Suggested heading:

```md
## [0.1.0] - 2026-04-29

Do not describe roadmap features as finished.

Release notes

Prepare release notes draft, either in report or in:

docs/releases/direm-v0.1.0.md

Release notes should include:

Summary
Added
Known limitations
Checks
Credits

Known limitations must include:

no retry scheduler;
no delivery history command;
no dashboard;
no webhook mode;
no AI translation;
no reminder editing.
Tests

Required automated checks:

python -m pytest
python -m compileall src alembic tests
docker compose config

Migration sanity:

docker compose run --rm bot alembic heads
docker compose run --rm bot alembic current
docker compose run --rm bot alembic upgrade head
docker compose run --rm bot alembic current

Git safety checks:

git status
git diff
git diff --cached
git ls-files .env
git status --ignored --short .docs-local DI-CODE docs/DI-CODE
Manual smoke

Use docs/RUNTIME_SMOKE.md.

Minimum owner runtime smoke before tag:

/start
/language → Қазақша → /help
/language → English → /help
/language → Русский → /help
/new → verify Cancel button → cancel
/timezone → set Asia/Almaty
/new → create near-due reminder
wait for worker delivery
/list
/pause via inline button
/resume via inline button
/delete via inline button + confirmation
verify deleted reminder disappears
Acceptance checklist
 Release branch starts from updated main.
 PR #3 / D016 help-copy micro-patch is merged.
 Automated checks pass.
 Migration checks pass.
 Runtime smoke checklist is current.
 README truth is preserved.
 CHANGELOG truth is preserved.
 Release notes are prepared.
 .env is not tracked.
 .docs-local/, DI-CODE/, and docs/DI-CODE/ are not staged.
 No new features were added.
 No release tag was created without explicit owner approval.
 Executor report includes branch, commit, changed files, checks, risks and push state.
Verification commands
python -m pytest
python -m compileall src alembic tests
docker compose config
docker compose run --rm bot alembic heads
docker compose run --rm bot alembic current
docker compose run --rm bot alembic upgrade head
docker compose run --rm bot alembic current
git status
git diff
git diff --cached
git ls-files .env
git status --ignored --short .docs-local DI-CODE docs/DI-CODE
Git / GitHub expectations
Follow DI-CODE_GITHUB_WORKFLOW.md.
Use release/direm-v0.1.0.
Do not commit directly to main.
Do not create tag until owner explicitly approves.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
Report branch, commits, changed files, checks, PR state and push state.
Implementation guard
Implement only this release pass.
Do not implement future roadmap items.
Do not add new product features.
Do not refactor unrelated areas.
Do not hide release-blocking bugs inside release docs.
Preserve versioning and credits metadata.
Update README and CHANGELOG only with truthful release-state wording.
Run required checks and report results.
If release readiness is blocked, stop and report the blocker.
Do not create release tag until owner explicitly approves.
Expected result summary

After this ticket:

DIREM v0.1.0 release state is verified;
release notes are prepared;
README/CHANGELOG are truthful;
automated checks pass;
migration state is verified;
repository is safe for release tag.

Still not implemented after this ticket:

retry scheduler;
AI translation;
delivery history;
dashboard;
webhook mode;
reminder editing;
web UI.
