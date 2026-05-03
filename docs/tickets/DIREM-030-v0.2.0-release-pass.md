# DIREM-030 — v0.2.0 Release Pass

## Status
Ready for implementation

## Version target
DIREM v0.2.0

## Workstream
Docs / Release

## Recommended branch
release/direm-v0.2.0

## Purpose

Prepare DIREM v0.2.0 release after the post-v0.1.0 feature batch.

This is a release pass only. Do not add product features.

## Source of truth

Read before implementation:

- README.md
- CHANGELOG.md
- docs/RUNTIME_SMOKE.md
- docs/ROADMAP.md
- docs/BACKLOG.md
- docs/DECISIONS.md
- docs/releases/direm-v0.1.0.md
- docs/tickets/DIREM-030-v0.2.0-release-pass.md

DI-CODE reference:
- `.docs-local/DI-CODE/DI-CODE_CANON.md`
- `.docs-local/DI-CODE/DI-CODE_GITHUB_WORKFLOW.md`
- `.docs-local/DI-CODE/DI-CODE_TICKET_HANDOFF_PLAYBOOK.md`
- `.docs-local/DI-CODE/DI-CODE_COMMIT-ATTRIBUTION.md`

Do not stage, commit or push `.docs-local/`, `DI-CODE/`, or `docs/DI-CODE/`.

## Current release baseline

Released:

- `direm-v0.1.0`

Expected included changes since v0.1.0:

- lightweight first-run onboarding;
- expanded timezone picker with curated region lists;
- localized main menu and hubs;
- stale Dorpheus cleanup;
- Bunker Mode design;
- Bunker state foundation;
- worker suppression for Bunker-active users;
- Telegram Bunker UX;
- Bunker deactivation rescheduling;
- home status reminder stats;
- direct Bunker ON/OFF reply-keyboard toggle;
- README hero image.

## Scope

In scope:

- verify `main` includes all accepted work through D029;
- run final automated checks;
- run Alembic migration sanity checks;
- verify README truth;
- verify CHANGELOG truth;
- verify RUNTIME_SMOKE truth;
- prepare `docs/releases/direm-v0.2.0.md`;
- finalize CHANGELOG section for `0.2.0`;
- verify `.env` is not tracked;
- verify `.docs-local/`, `DI-CODE/`, `docs/DI-CODE/` are not staged;
- verify README hero image asset is intentionally tracked and no old `images/` folder is tracked;
- report whether `direm-v0.2.0` tag is safe to create.

Out of scope:

- new features;
- Bunker history;
- timed Bunker;
- per-reminder snooze;
- delivery history;
- retry scheduler;
- reminder editing;
- dashboard/webhook;
- AI/web UI;
- release tag creation unless owner explicitly approves after review.

## CHANGELOG

Finalize `[Unreleased]` into:

```md
## [0.2.0] - 2026-05-03

Keep only truthful completed items.

After finalization, leave a fresh:

## [Unreleased]

above it if the changelog style supports that.

Release notes

Create:

docs/releases/direm-v0.2.0.md

Include:

Summary
Added
Changed
Known limitations
Checks
Credits

Known limitations must include:

no timed Bunker;
no per-reminder snooze;
no Bunker history;
no delivery history command;
no retry scheduler;
no reminder editing;
no dashboard/webhook;
no AI/web UI.
Checks

Required:

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
git ls-files images
git ls-files docs/assets
Manual smoke

Use docs/RUNTIME_SMOKE.md.

Minimum owner smoke before tag:

/start;
verify home status stats;
verify Bunker OFF/ON direct reply toggle;
verify Bunker suppresses due reminder delivery;
verify turning Bunker off reschedules active reminders without catch-up;
/timezone → other regions → Russia/Europe/Asia/America/UTC;
/new;
/list;
/pause;
/resume;
/delete;
/version;
/credits.
Acceptance checklist
 Release branch starts from updated main.
 D029 is merged before release branch starts.
 Automated checks pass.
 Alembic checks pass.
 README is truthful.
 CHANGELOG is finalized for 0.2.0.
 Release notes are prepared.
 Runtime smoke checklist matches current behavior.
 .env is not tracked.
 Local DI-CODE refs are not staged.
 README hero asset is tracked intentionally.
 Old images/ folder is not tracked.
 No new features were added.
 No release tag was created without owner approval.
 Executor reports branch, commit, changed files, checks and tag safety.
Implementation guard

Design/release pass only.

Do not implement product features.
Do not create release tag.
Do not modify runtime behavior.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
If a release blocker appears, stop and report.