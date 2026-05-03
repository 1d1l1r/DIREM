# DIREM-027 — Home Status and Bunker Keyboard Polish

## Status
Ready for implementation

## Version target
DIREM v0.2.0 — Bunker UX polish

## Recommended branch
feature/DIREM-027-home-status-bunker-keyboard-polish

## Purpose

Polish the Telegram home/status screen and Bunker placement after D026 runtime smoke.

Bunker Mode is implemented, but its UI placement should change:
- main menu inline buttons should stay focused on navigation;
- Bunker should become the bottom idle reply-keyboard quick action;
- Cancel/Back should return the user to the main status screen;
- the main status screen should show useful reminder stats.

## Scope

Need:

- remove Bunker inline button from the main menu message;
- main menu inline buttons should remain:
  - List
  - Settings
  - Help

- idle/top-level reply keyboard should show localized Bunker state/action:
  - ru: `Бункер OFF` / `Бункер ON`
  - kk/en equivalents;

- pressing the Bunker reply button should immediately toggle Bunker:
  - OFF → activate Bunker;
  - ON → deactivate Bunker and reschedule active reminders using existing D026 behavior;
  - no confirmation screen before toggle;

- after toggle, bot should send:
  - localized confirmation;
  - updated main status screen;

- active FSM flows should still show localized Cancel reply button instead of Bunker;

- Cancel behavior:
  - pressing Cancel exits active flow;
  - after cancel, show the main status screen;

- Back behavior:
  - Back from hubs returns to the main status screen;

- main status screen should show:
  - DIREM activated text;
  - purpose line;
  - current timezone;
  - current language;
  - Bunker state;
  - reminder stats:
    - total non-deleted reminders;
    - active reminders;
    - paused/stopped reminders;

- stats must be scoped to current Telegram user;
- localize new/changed copy for ru/kk/en;
- update tests;
- update README/RUNTIME_SMOKE/CHANGELOG only as needed.

## Suggested Russian main status

```text
DIREM активирована.

Я помогу регулярно возвращаться к намерению.

Текущий часовой пояс: Asia/Almaty
Язык: 🇷🇺 Русский
Бункер: выключен

Напоминаний: 4
Активно: 2
Остановлено: 2

Inline buttons:

[Список] [Настройки] [Помощь]

Reply keyboard:

[Бункер OFF]

or:

[Бункер ON]
Suggested toggle confirmations
Бункер активирован.
DIREM временно не будет отправлять напоминания.
Бункер выключен.
Активные напоминания перепланированы без догоняющей рассылки.
Out of scope

Do not implement:

timed Bunker;
per-reminder snooze;
Bunker history;
delivery history;
retries;
reminder editing;
dashboard/webhook;
AI/web UI;
migrations unless absolutely required.
Checks
python -m pytest
python -m compileall src alembic tests
docker compose config
git status
git diff
Acceptance
Main menu inline buttons are only List / Settings / Help.
Idle reply keyboard shows Bunker ON/OFF.
Pressing Bunker ON/OFF toggles Bunker directly.
Toggle sends confirmation and updated main status screen.
Active flows still show Cancel.
Cancel returns to main status screen after exiting a flow.
Back returns to main status screen from hubs.
Main status screen shows reminder stats for current user.
Existing /bunker command still works.
Existing commands still work.
Tests pass.