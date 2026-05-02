# DIREM-020 — Timezone Picker UX

## Status
Implemented

## Version target
`DIREM v0.1.1 — UX polish`

## Workstream
General

## Recommended branch
`feature/DIREM-020-timezone-picker-ux`

## Owner / Contributors

Project Owner:
- 1D1L1R

Contributors for this ticket:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — implementation executor

## Purpose

Improve `/timezone` UX.

Current `/timezone` works with manual IANA timezone input, but many users do not know names like `Asia/Almaty`. This ticket adds a lightweight Telegram picker while preserving manual input.

After this ticket, users should be able to set timezone through buttons for common cases, without needing to know IANA names.

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
- docs/tickets/DIREM-020-timezone-picker-ux.md

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

Accepted after release:
- DIREM-018 — post-release backlog planning
- DIREM-019 — guided first-run onboarding

Current behavior:
- `/timezone` stores a validated IANA timezone.
- Existing user timezone is preserved on repeated `/start`.
- UI is localized for ru/kk/en.
- `/language`, `/new`, `/list`, `/pause`, `/resume`, `/delete`, `/cancel` work.
- Help/Cancel reply keyboard exists.
- Inline buttons are used in several flows.

## Scope

### In scope

Improve `/timezone` with a lightweight inline picker.

Need:

- keep existing manual IANA input support;
- show inline timezone choices for common cases;
- include prominent Kazakhstan options:
  - `Asia/Almaty`
  - `Asia/Aqtau`
  - `Asia/Aqtobe`
  - `Asia/Oral`
  - `Asia/Qyzylorda`
- include UTC/GMT offset shortcuts where safe and mappable to stable IANA zones or fixed UTC behavior if already supported;
- include “manual input” path;
- include “cancel” path or reuse `/cancel`;
- localize timezone picker prompts for ru/kk/en;
- make invalid timezone recovery clearer;
- preserve current DB model;
- no migration unless absolutely required;
- add tests;
- update README if needed;
- update RUNTIME_SMOKE;
- update CHANGELOG.

### Suggested UX

`/timezone` should show current timezone and options:

```text
Current timezone: Asia/Almaty

Choose timezone:
[🇰🇿 Almaty / Astana — Asia/Almaty]
[🇰🇿 Aqtau — Asia/Aqtau]
[🇰🇿 Aqtobe — Asia/Aqtobe]
[🇰🇿 Oral — Asia/Oral]
[🇰🇿 Qyzylorda — Asia/Qyzylorda]
[UTC]
[Enter manually]

Manual input remains valid:

Asia/Almaty
Europe/London
America/New_York
UTC
Out of scope

Do not implement:

full country/continent browser;
automatic timezone detection;
geolocation request;
Telegram WebApp timezone detection;
timezone guessing as automatic setting;
new reminder features;
reminder editing;
delivery history;
retries;
dashboard/webhook;
AI features;
web UI;
migrations unless absolutely necessary.

Future/parked work:

full region/country timezone browser;
geolocation-based timezone suggestion;
language-based timezone suggestions;
Telegram WebApp timezone detection.
Technical requirements
Reuse existing timezone validation.
Keep handlers thin.
Reuse existing i18n helper.
Callback data must be short and safe.
Stale/invalid callback data must not crash the bot.
Manual input fallback must remain available.
Existing /timezone tests should still pass.
User behavior

When user sends /timezone:

bot shows current timezone if available;
bot offers common timezone buttons;
bot offers manual input;
choosing a button saves timezone;
manual input still works;
invalid manual input gives clear localized error and recovery hint.
Localization / copy behavior

Supported languages:

ru;
kk;
en.

Timezone identifiers such as Asia/Almaty should remain untranslated.

Data / model changes

Expected:

No data/model changes.
No migration.

If implementation appears to require DB changes, stop and report first.

README update

README may say:

/timezone supports manual IANA input and common timezone buttons.

README must not claim:

automatic timezone detection;
full country/continent browser;
geolocation;
system timezone extraction from Telegram.
CHANGELOG update

Add under [Unreleased]:

- Added lightweight `/timezone` picker with common timezone buttons while preserving manual IANA input.
Tests

Required tests:

/timezone renders picker options;
choosing Asia/Almaty persists timezone;
choosing another Kazakhstan timezone persists timezone;
manual IANA input still works;
invalid input returns localized recovery message;
stale/invalid callback does not crash;
existing /start timezone preservation still works.
Manual smoke
/timezone
tap Asia/Almaty
/timezone
tap Enter manually
Europe/London
/timezone
send invalid timezone
/cancel

Expected:

timezone buttons work;
manual input still works;
invalid input is handled clearly;
no migration is required;
existing reminder flows still work.
Acceptance checklist
 /timezone has inline picker options.
 Manual IANA input still works.
 Kazakhstan common timezones are available.
 Invalid timezone recovery is clearer.
 ru/kk/en text exists.
 No full country/continent browser was added.
 No automatic timezone detection was claimed.
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
Use feature/DIREM-020-timezone-picker-ux.
Do not commit directly to main.
Do not create a release tag.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
Report branch, commit, changed files, checks and push state.
Implementation guard
Implement only this timezone picker UX ticket.
Do not implement full country/continent browser.
Do not implement automatic timezone detection.
Do not request geolocation.
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

users can set timezone through common inline buttons;
Kazakhstan timezones are easy to find;
manual IANA input remains available;
timezone UX is easier without adding heavy timezone infrastructure.
