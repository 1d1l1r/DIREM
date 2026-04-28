# DIREM-015 — Language Selection and i18n Foundation

## Status
Ready for implementation

## Version target
`DIREM v0.1.0 — Core MVP`

## Recommended branch
`feature/DIREM-015-language-selection-i18n-foundation`

## Owner / Contributors

Project Owner:
- 1D1L1R

Contributors for this ticket:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — implementation executor

## Purpose

Add multilingual UX foundation for DIREM.

DIREM is Telegram-first and local-aware. This ticket adds language selection and initial maintained localization for:

- Russian;
- Kazakh;
- English.

This ticket should make DIREM multilingual by design without adding new reminder product features.

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
- DI-CODE_CANON.md
- DI-CODE_GITHUB_WORKFLOW.md
- DI-CODE_COMMIT-ATTRIBUTION.md

## Current state / Dependencies

Assume these tickets are complete:

- DIREM-001 — project skeleton
- DIREM-002 — domain model / database schema
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

Current behavior:

- `/start` creates or updates user;
- `/timezone` stores IANA timezone;
- `/new` creates reminders;
- `/list` shows reminders;
- `/pause`, `/resume`, `/delete` work with inline buttons and manual fallback;
- `/cancel` exits FSM flows;
- worker sends due active reminders;
- retries/history/dashboard/webhook are not implemented.

## Scope

### In scope

Add language selection and i18n foundation.

Need:

- add `language_code` to user persistence;
- support language codes:
  - `ru`
  - `kk`
  - `en`
- default user language:
  - use Telegram `from_user.language_code` if supported;
  - fallback to `ru`;
- preserve existing user language on repeated `/start`;
- add `/language` command;
- add `/language` to Telegram command menu;
- add `/language` to `/help`;
- `/language` should show inline buttons:
  - 🇷🇺 Русский
  - 🇰🇿 Қазақша
  - 🇬🇧 English
- selected language should persist to DB;
- after language change, bot should respond in selected language;
- add i18n catalog/module, for example:
  - `src/direm/i18n/__init__.py`
  - `src/direm/i18n/catalog.py`
  - or equivalent clean structure;
- route user-facing bot strings through i18n helper where practical for current MVP flows;
- cover at least these user-facing areas:
  - `/start`
  - `/help`
  - `/timezone`
  - `/new`
  - `/list`
  - `/pause`
  - `/resume`
  - `/delete`
  - `/cancel`
  - `/version`
  - `/credits`
  - worker delivery wrapper text
  - validation/error/fallback messages in existing flows
- keep reminder user content unchanged:
  - do not translate reminder title;
  - do not translate reminder message text;
- update README;
- update RUNTIME_SMOKE;
- update CHANGELOG;
- add tests.

### Translation tone

Russian:

- clear, friendly, not over-formal.

Kazakh:

- clear, natural interface Kazakh;
- project-maintained initial localization;
- use “ниет” where it fits the DIREM concept;
- avoid awkward over-literal translations.

English:

- clear and simple.

Suggested core phrases:

```text
ru: Вернуться к намерению.
kk: Ниетке қайта оралу.
en: Return to intention.
ru: Напоминание создано.
kk: Еске салу жасалды.
en: Reminder created.
ru: Нені еске салайын?  # wrong language intentionally not allowed

Correct language separation:

ru: Что напомнить?
kk: Нені еске салайын?
en: What should I remind you about?
Out of scope

Do not implement:

new reminder features;
reminder editing;
retry scheduler;
delivery history command;
dashboard;
webhook mode;
Redis/Celery;
AI features;
web UI;
voice/audio;
automatic translation of user reminder content;
complex per-chat/per-group language scopes;
separate admin UI;
full gettext/Babel stack unless clearly justified;
broad unrelated refactor.
Technical requirements
add Alembic migration for users.language_code;
default existing users to ru unless project code already has a better safe default;
validate language codes centrally;
avoid hardcoding user-facing strings directly in handlers where this ticket touches current MVP text;
keep i18n helper simple and testable;
missing translation keys should fail loudly in tests or fall back predictably;
avoid introducing heavy dependencies;
keep handlers thin;
services may receive language code or translation helper where appropriate;
command menu registration should include /language;
Telegram command descriptions may remain default-language only unless localization is simple and safe.
Data/model changes

Add field:

users.language_code

Expected values:

ru
kk
en

Default:

ru
User behavior
/start

New user:

stores user;
stores timezone as before;
stores language from Telegram if supported, otherwise ru;
replies in selected/default language.

Existing user:

preserves timezone;
preserves language unless user changes it through /language.
/language

User sees inline buttons:

🇷🇺 Русский
🇰🇿 Қазақша
🇬🇧 English

After choosing:

language is saved;
bot confirms in the selected language;
later commands use that language.
Worker delivery

Worker should keep user reminder title/message as written.

If there is wrapper text, it should use the user language.

Example:

ru: Напоминание:
kk: Еске салу:
en: Reminder:
README update

README may say:

DIREM supports language selection via /language;
supported languages are Russian, Kazakh and English;
user reminder text is not auto-translated;
worker delivery uses the user’s selected interface language for wrapper text if applicable.

README must not claim:

AI translation;
complete professional human localization;
per-chat language scopes;
dashboard/web UI.
RUNTIME_SMOKE update

Add language smoke:

/start
/language
select Қазақша
/help
/language
select English
/help
/language
select Русский
/help

Then continue existing reminder smoke.

CHANGELOG update

Add truthful bullets for:

language selection;
users.language_code;
ru/kk/en i18n foundation;
command menu update for /language.
Tests

Need tests for:

language code validation;
default language from Telegram language code;
fallback to ru;
repeated /start preserves existing language;
/language persists selected language;
i18n catalog contains required keys for ru, kk, en;
selected language affects at least /help or core response rendering;
worker delivery wrapper uses user language if wrapper text exists;
existing reminder flows still pass.
Acceptance checklist
 users.language_code exists and is migrated.
 New users get supported Telegram language or fallback ru.
 Repeated /start preserves existing language.
 /language exists.
 /language uses inline buttons.
 Russian, Kazakh and English are supported.
 /help reflects /language.
 Telegram command menu includes /language.
 Existing flows still work.
 Reminder title/message text is not auto-translated.
 Worker delivery behavior remains unchanged except localized wrapper text if present.
 README is truthful.
 RUNTIME_SMOKE includes language checks.
 CHANGELOG is updated.
 Tests pass.
Verification commands
python -m pytest
python -m compileall src alembic tests
docker compose config
Optional runtime smoke

Only if real Telegram bot token is configured:

/start
/language
tap 🇰🇿 Қазақша
/help
/language
tap 🇬🇧 English
/help
/language
tap 🇷🇺 Русский
/help
/new
/list
/pause
/resume
/delete

Expected:

/language buttons work;
selected language persists;
/help changes language;
existing reminder flows still work;
worker delivery still works;
no user reminder content is auto-translated.
Implementation guard
Implement only this ticket.
Do not implement future roadmap items.
Do not refactor unrelated areas unless required for i18n extraction.
Do not add heavy localization infrastructure unless justified in the plan.
Do not add dashboard/webhook/AI/retries/history.
Do not translate user-authored reminder title/message.
Preserve versioning and credits metadata.
Update README and CHANGELOG only with truthful current-state wording.
Run required checks and report results.
If docs/ticket/code conflict, stop and report the conflict.
Expected result summary

After this ticket:

DIREM has persisted per-user language preference;
users can choose Russian, Kazakh or English;
current MVP bot UX is localized through a simple i18n foundation;
existing reminder creation/control/delivery behavior remains intact.