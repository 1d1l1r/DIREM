# DIREM-022 — Telegram Main Menu and Hubs

## Status
Implemented

## Version target
`DIREM v0.1.1 — UX polish`

## Workstream
General

## Recommended branch
`feature/DIREM-022-telegram-main-menu-and-hubs`

## Owner / Contributors

Project Owner:
- 1D1L1R

Contributors for this ticket:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — implementation executor

## Purpose

Add a clearer Telegram navigation layer for DIREM.

DIREM currently works through commands and inline buttons, but the user experience should feel more like a small Telegram-first application than a command list.

This ticket adds:
- a main screen after `/start`;
- top-level navigation buttons;
- lightweight menu hubs for reminders, settings and help;
- localized copy for ru/kk/en.

This is UX/navigation polish. It must not add new reminder product features.

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
- docs/tickets/DIREM-022-telegram-main-menu-and-hubs.md

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

- `direm-v0.1.0` — Core MVP release
- DIREM-018 — post-release backlog planning
- DIREM-019 — guided first-run onboarding
- DIREM-020 — timezone picker UX
- DIREM-021 — Dorpheus copy cleanup

Current behavior:

- `/start` creates or updates user.
- First-time `/start` shows lightweight onboarding.
- `/language` selects ru/kk/en.
- `/timezone` has lightweight picker and manual IANA input.
- `/new`, `/list`, `/pause`, `/resume`, `/delete` work.
- `/help` is grouped and localized.
- Help/Cancel reply keyboard exists.
- Inline reminder control buttons exist.

## Scope

### In scope

Add a localized Telegram main menu and simple hubs.

Need:

- update `/start` to show a main screen for existing users;
- preserve first-run onboarding behavior for new users;
- main screen should show:
  - DIREM activated/status text;
  - short purpose line;
  - current timezone;
  - selected language;
  - top-level inline buttons:
    - List;
    - Settings;
    - Help;
- add callbacks/handlers for top-level menu buttons;
- add Reminder/List hub:
  - message about reminder actions;
  - buttons:
    - Add;
    - Pause;
    - Resume;
    - Delete;
    - Back/Home;
- add Settings hub:
  - message about settings;
  - buttons:
    - Language;
    - Timezone;
    - Back/Home;
- add Help hub:
  - show or reuse grouped help text;
  - buttons:
    - DIREM version;
    - Credits;
    - Back/Home;
- hub buttons should route to existing flows/handlers where practical:
  - Add → `/new` flow;
  - Pause → existing `/pause`;
  - Resume → existing `/resume`;
  - Delete → existing `/delete`;
  - Language → existing `/language`;
  - Timezone → existing `/timezone`;
  - Version → existing `/version`;
  - Credits → existing `/credits`;
- localize all new menu text/buttons for:
  - ru;
  - kk;
  - en;
- keep command-based access working;
- preserve existing inline buttons for language/timezone/reminder control;
- update README if needed;
- update RUNTIME_SMOKE;
- update CHANGELOG;
- add tests.

### Main screen Russian copy

Use this direction for Russian:

```text
DIREM активирована.

Я помогу регулярно возвращаться к намерению.

Текущий часовой пояс: Asia/Almaty
Язык: 🇷🇺 Русский

Buttons:

[Список] [Настройки] [Помощь]
Reminder hub Russian direction
Напоминания и действия.

Выберите, что сделать:

Buttons:

[Добавить] [Остановить]
[Возобновить] [Удалить]
[Назад]
Settings hub Russian direction
Настройки DIREM.

Здесь можно изменить язык и часовой пояс.

Buttons:

[Язык] [Часовой пояс]
[Назад]
Help hub Russian direction

Reuse grouped help text where practical.

Buttons:

[Версия DIREM] [Авторы]
[Назад]
Out of scope

Do not implement:

Bunker mode;
global pause;
status snapshot/restore;
advanced timezone browser;
GMT offset parser;
automatic timezone detection;
geolocation;
WebApp timezone detection;
new reminder features;
reminder editing;
delivery history;
retries;
dashboard/webhook;
AI features;
web UI;
migrations unless absolutely required.

Future/parked work:

Bunker Mode;
Advanced Timezone UX;
Reminder Editing;
Delivery History;
Retry Policy MVP.
Technical requirements
Keep handlers thin.
Reuse existing services/handlers where practical.
Use i18n catalog for all user-facing menu copy.
Callback data must be short and safe.
Stale/invalid callbacks must not crash the bot.
Do not break existing commands.
Do not remove Help/Cancel reply keyboard behavior.
Prefer no data/model changes.
If a migration appears necessary, stop and report first.
User behavior

Existing user sends /start:

receives main DIREM screen;
sees timezone and language;
can tap List / Settings / Help.

New user sends /start:

still receives first-run guidance;
should have access to main menu actions or clear next actions.

User taps List:

sees reminder action hub;
can enter existing reminder flows.

User taps Settings:

sees language/timezone hub;
can enter existing settings flows.

User taps Help:

sees help/about hub;
can open version or credits.
Localization / copy behavior

Supported languages:

ru;
kk;
en.

Do not translate:

IANA timezone identifiers;
user-authored reminder title/message.
Data / model changes

Expected:

No data/model changes.
No migration.

If implementation requires data/model changes, stop and report.

README update

README may say:

/start shows a main menu with List, Settings and Help;
menu buttons route to existing flows.

README must not claim:

Bunker mode;
advanced timezone browser;
reminder editing;
retry scheduler;
delivery history;
dashboard/webhook;
AI features.
CHANGELOG update

Add under [Unreleased]:

- Added localized Telegram main menu and navigation hubs for reminders, settings and help.
Tests

Required tests:

/start main screen renders for existing users;
first-run onboarding still works for new users;
main menu buttons are present/localized for ru/kk/en;
List hub renders expected buttons;
Settings hub renders expected buttons;
Help hub renders expected buttons;
hub action buttons route to existing flows or callbacks;
invalid/stale callback does not crash;
existing command handlers still pass.
Manual smoke
/start
tap Список
tap Назад
tap Настройки
tap Язык
/cancel
/start
tap Настройки
tap Часовой пояс
/cancel
/start
tap Помощь
tap Версия DIREM
/start
tap Помощь
tap Авторы

Expected:

main menu appears;
hubs appear;
buttons route to existing flows;
back/home returns to main screen;
existing commands still work.
Acceptance checklist
 /start shows main screen for existing users.
 First-run onboarding is preserved.
 Main screen shows timezone and language.
 List hub exists.
 Settings hub exists.
 Help hub exists.
 All new copy is localized for ru/kk/en.
 Existing command access still works.
 Existing inline buttons still work.
 No Bunker mode was added.
 No advanced timezone browser was added.
 No migrations were added.
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
Use feature/DIREM-022-telegram-main-menu-and-hubs.
Do not commit directly to main.
Do not create a release tag.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
Report branch, commit, changed files, checks and push state.
Implementation guard
Implement only this menu/hub UX ticket.
Do not implement Bunker mode.
Do not implement global pause or status snapshot/restore.
Do not implement advanced timezone browser.
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

/start becomes a useful home screen;
users can navigate DIREM through top-level buttons;
reminder, settings and help actions are discoverable;
Bunker mode remains a separate future feature.
