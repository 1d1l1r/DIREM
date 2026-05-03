# DIREM-021 — Dorpheus Copy Cleanup

## Status
Implemented

## Version target
`DIREM v0.1.1 — UX polish`

## Workstream
Docs / General

## Recommended branch
`docs/DIREM-021-dorpheus-copy-cleanup`

## Owner / Contributors

Project Owner:
- 1D1L1R

Contributors for this ticket:
- Rein Hard V — scope lock, review
- Bushid Ronin V — cleanup executor

## Purpose

Remove stale `Dorpheus` references from DIREM copy, examples and tests.

`Dorpheus` does not belong to this bot and should not appear in user-facing examples or project docs unless explicitly retained as historical context.

## Source of truth

Read before implementation:

- docs/CONCEPT.md
- docs/ROADMAP.md
- docs/BACKLOG.md
- docs/tickets/DIREM-021-dorpheus-copy-cleanup.md

DI-CODE reference:
- `.docs-local/DI-CODE/DI-CODE_CANON.md`
- `.docs-local/DI-CODE/DI-CODE_GITHUB_WORKFLOW.md`
- `.docs-local/DI-CODE/DI-CODE_TICKET_HANDOFF_PLAYBOOK.md`
- `.docs-local/DI-CODE/DI-CODE_COMMIT-ATTRIBUTION.md`

Important:
- Follow the active ticket first.
- Do not stage, commit or push `.docs-local/`, `DI-CODE/`, or `docs/DI-CODE/`.

## Current known references

Previously found references:

- `docs/CONCEPT.md`
- `docs/tickets/DIREM-005-create-reminder-flow.md`
- `src/direm/i18n/catalog.py`
- `tests/unit/test_new_handler.py`
- `tests/unit/test_reminder_service.py`

Executor must re-scan the repository before patching.

## Scope

### In scope

- search the repository for:
  - `Dorpheus`
  - `dorpheus`
  - `DORPHEUS`
- remove or replace those references where they are stale DIREM examples;
- replace user-facing example text with DIREM-neutral copy;
- update tests that use `Dorpheus` as fixture text;
- keep old ticket docs readable if edited;
- do not change product behavior.

Suggested replacements:

- `Dorpheus focus` → `Morning focus`
- `Intent: “Dorpheus”` → `Intent: “Morning focus”`
- `Фокус: Dorpheus` → `Фокус: утренний настрой`

### Out of scope

Do not implement:

- new UX;
- timezone picker changes;
- main menu shell;
- bunker mode;
- reminder features;
- i18n architecture changes;
- migrations;
- worker changes;
- release tag changes.

## Technical requirements

- No behavior changes.
- No data/model changes.
- No migration.
- Tests should still pass.
- If any `Dorpheus` reference is intentionally retained, report why.

## README update

No README update required unless `Dorpheus` appears there.

## CHANGELOG update

Add under `[Unreleased]`:

```text
- Removed stale `Dorpheus` references from DIREM examples and tests.
Tests

Required:

existing tests pass;
update exact string assertions if needed.
Verification commands
python -m pytest
python -m compileall src alembic tests
docker compose config
git status
git diff

Also run a final search:

rg -n "Dorpheus|dorpheus|DORPHEUS" .

If rg is unavailable, use PowerShell Select-String.

Acceptance checklist
 No unintended Dorpheus references remain.
 User-facing examples are DIREM-neutral.
 Tests pass.
 CHANGELOG is updated.
 No product behavior changed.
 No local DI-CODE reference docs were staged.
 No release tag was created.
Implementation guard
Implement only this copy cleanup.
Do not change product behavior.
Do not add new features.
Do not refactor unrelated code.
Do not change timezone picker behavior.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
If a reference seems historical and should remain, report it before keeping it.
Expected result summary

After this ticket:

DIREM no longer leaks stale Dorpheus naming in examples/tests;
project copy is cleaner before further UX work.
