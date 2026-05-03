# DIREM-028 — Timezone Picker v2: Other Regions and UTC/GMT Clarity

## Status
Ready for implementation

## Version target
DIREM v0.2.0 — UX polish

## Workstream
General / UX Polish

## Recommended branch
feature/DIREM-028-timezone-picker-v2

## Purpose

Improve `/timezone` so users do not need to know IANA timezone names.

Current `/timezone` has Kazakhstan shortcuts, UTC (GMT+0), and manual IANA input. It works technically, but runtime smoke showed that it is still unclear for users outside Kazakhstan or users who do not know what to type manually.

This ticket adds an “Other timezones” path with curated region lists and clearer UTC/GMT wording.

## Source of truth

Read before implementation:

- docs/CONCEPT.md
- docs/ARCHITECTURE.md
- docs/DECISIONS.md
- docs/BACKLOG.md
- docs/ROADMAP.md
- docs/RUNTIME_SMOKE.md
- docs/tickets/DIREM-028-timezone-picker-v2.md

DI-CODE reference:
- `.docs-local/DI-CODE/DI-CODE_CANON.md`
- `.docs-local/DI-CODE/DI-CODE_GITHUB_WORKFLOW.md`
- `.docs-local/DI-CODE/DI-CODE_TICKET_HANDOFF_PLAYBOOK.md`
- `.docs-local/DI-CODE/DI-CODE_COMMIT-ATTRIBUTION.md`

Important:

- Follow the active ticket first.
- Use DI-CODE_GITHUB_WORKFLOW.md for branch/commit/push rules.
- Do not stage, commit or push `.docs-local/`, `DI-CODE/`, or `docs/DI-CODE/`.

## Current behavior

`/timezone` currently supports:

- Kazakhstan timezone buttons;
- `UTC (GMT+0)`;
- manual IANA input;
- invalid timezone recovery.

Problem:

- users do not know which IANA name to enter;
- UTC/GMT meaning is still not clear enough;
- there is no “Other” path for Russia, Europe, Asia, America, etc.

## Scope

### In scope

Improve `/timezone` picker with a curated second-level region flow.

Need:

- keep current popular Kazakhstan shortcuts;
- keep manual IANA input;
- keep `UTC` as stored DB value for UTC;
- show UTC to user as `UTC / GMT+0` or equivalent localized copy;
- add button:
  - ru: `Другие часовые пояса`
  - kk equivalent;
  - en: `Other time zones`;
- add region picker:
  - Kazakhstan;
  - Russia;
  - Europe;
  - Asia;
  - America;
  - UTC / GMT;
  - Back;
- add curated timezone lists for each region;
- selecting any timezone saves the correct IANA timezone value;
- after saving, confirmation should show both human-readable label and stored IANA value where useful;
- localize all user-facing copy for ru/kk/en;
- stale/invalid callbacks should not crash;
- update tests;
- update README/RUNTIME_SMOKE/CHANGELOG if needed.

### Suggested top-level `/timezone` screen

```text
Текущий часовой пояс: Asia/Almaty

Популярные варианты:
[Asia/Almaty]
[Asia/Aqtau]
[Asia/Aqtobe]
[Asia/Oral]
[Asia/Qyzylorda]
[UTC / GMT+0]
[Другие часовые пояса]
[Ввести вручную]
Suggested “Other time zones” screen
Выберите регион:

[Казахстан]
[Россия]
[Европа]
[Азия]
[Америка]
[UTC / GMT]
[Назад]
Kazakhstan list

Use current options:

Asia/Almaty
Asia/Aqtau
Asia/Aqtobe
Asia/Oral
Asia/Qyzylorda
Russia list

Curated options:

Moscow — Europe/Moscow
Yekaterinburg — Asia/Yekaterinburg
Novosibirsk — Asia/Novosibirsk
Krasnoyarsk — Asia/Krasnoyarsk
Irkutsk — Asia/Irkutsk
Yakutsk — Asia/Yakutsk
Vladivostok — Asia/Vladivostok
Kamchatka — Asia/Kamchatka
Europe list

Curated options:

London — Europe/London
Berlin / Paris / Rome — Europe/Berlin
Warsaw — Europe/Warsaw
Helsinki — Europe/Helsinki
Istanbul — Europe/Istanbul
Asia list

Curated options:

Tashkent — Asia/Tashkent
Dubai — Asia/Dubai
Tbilisi — Asia/Tbilisi
Tokyo — Asia/Tokyo
Seoul — Asia/Seoul
Shanghai — Asia/Shanghai
Singapore — Asia/Singapore
Bangkok — Asia/Bangkok
America list

Curated options:

New York — America/New_York
Chicago — America/Chicago
Denver — America/Denver
Los Angeles — America/Los_Angeles
Toronto — America/Toronto
Mexico City — America/Mexico_City
São Paulo — America/Sao_Paulo
UTC / GMT screen

Clarify:

UTC / GMT+0 — нулевой часовой пояс без смещения.

Button:

UTC / GMT+0 → stores UTC

Do not implement free GMT+3 / GMT-5 parser in this ticket.

Out of scope

Do not implement:

full world timezone browser with all IANA zones;
country database;
automatic timezone detection;
geolocation request;
Telegram WebApp timezone detection;
free GMT offset parser;
timezone guessing from language;
migrations;
reminder features;
Bunker mechanics;
delivery history;
retries;
editing;
dashboard/webhook;
AI/web UI.
Technical requirements
Keep stored values as valid IANA timezone strings.
UTC / GMT+0 button stores UTC.
Region/city labels are user-facing only.
Reuse existing timezone validation.
Keep handlers thin.
Callback data must be short and safe.
Manual input fallback must remain available.
Invalid manual input recovery from D020 must remain intact.
No migration expected.
Confirmation behavior

After selecting a timezone button:

Часовой пояс обновлён: Europe/Moscow

For UTC, prefer clearer copy:

Часовой пояс обновлён: UTC / GMT+0

Stored value remains:

UTC
README update

README may say:

/timezone supports common timezone buttons, region lists and manual IANA input.

README must not claim:

automatic detection;
geolocation;
full world timezone database;
GMT offset parser;
system timezone extraction from Telegram.
CHANGELOG update

Add under [Unreleased]:

- Expanded `/timezone` picker with curated region lists and clearer UTC/GMT wording.
Tests

Required tests:

top-level timezone picker includes Other time zones;
Other time zones opens region list;
Russia region renders expected options;
Europe region renders expected options;
Asia region renders expected options;
America region renders expected options;
UTC / GMT screen explains UTC;
selecting Europe/Moscow persists Europe/Moscow;
selecting Europe/London persists Europe/London;
selecting Asia/Tokyo persists Asia/Tokyo;
selecting America/New_York persists America/New_York;
selecting UTC / GMT+0 persists UTC;
manual IANA input still works;
invalid manual input still recovers clearly;
stale/invalid callback does not crash;
ru/kk/en i18n coverage includes new keys.
Manual smoke
/timezone
tap Другие часовые пояса
tap Россия
tap Moscow / Europe/Moscow
/timezone
tap Другие часовые пояса
tap Europe
tap London / Europe/London
/timezone
tap Другие часовые пояса
tap Asia
tap Tokyo / Asia/Tokyo
/timezone
tap Другие часовые пояса
tap America
tap New York / America/New_York
/timezone
tap UTC / GMT
tap UTC / GMT+0
/timezone
tap Ввести вручную
Europe/Madrid
/timezone
send invalid timezone
/cancel

Expected:

region lists work;
selected zones persist;
UTC copy is clear;
manual input remains available;
invalid input is recoverable;
no full browser or autodetection is claimed.
Acceptance checklist
 /timezone has Other time zones path.
 Region picker exists.
 Kazakhstan, Russia, Europe, Asia, America and UTC/GMT lists exist.
 Selected timezone values persist as valid IANA strings.
 UTC is explained as UTC / GMT+0 but stored as UTC.
 Manual IANA input still works.
 Invalid input recovery still works.
 ru/kk/en copy exists.
 README truth is preserved.
 CHANGELOG truth is preserved.
 RUNTIME_SMOKE is updated.
 Tests pass.
 No migrations were added.
 No local DI-CODE reference docs were staged.
 No release tag was created.
Verification commands
python -m pytest
python -m compileall src alembic tests
docker compose config
git status
git diff
Implementation guard
Implement only Timezone Picker v2.
Do not implement full world timezone browser.
Do not implement automatic timezone detection.
Do not request geolocation.
Do not implement Telegram WebApp timezone detection.
Do not implement free GMT offset parser.
Do not change stored timezone semantics.
Do not add migrations.
Do not change Bunker behavior.
Do not implement reminder history/retries/editing/dashboard/webhook/AI/web UI.
Do not stage/commit/push .docs-local/, DI-CODE/, or docs/DI-CODE/.
Expected result summary

After this ticket:

/timezone becomes usable for people outside Kazakhstan;
UTC/GMT is clearer;
manual IANA input remains available;
DIREM still avoids heavy timezone infrastructure.