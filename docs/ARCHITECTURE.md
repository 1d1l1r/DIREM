# DIREM — Product Scope v0.1

## 0. Назначение документа

Этот документ фиксирует границы первого продукта DIREM.

Он отвечает на вопросы:

- что именно делаем в MVP;
- что сознательно не делаем;
- какие пользовательские сценарии считаются обязательными;
- какие фичи относятся к будущим версиям;
- по каким критериям MVP считается готовым.

`PRODUCT_SCOPE.md` должен использоваться implementation executor как ограничитель масштаба.

Главное правило:

> Если фича не описана в MVP scope — она не реализуется в текущем спринте, даже если выглядит логичной.

---

## 1. Продуктовая формула

**DIREM** — Telegram-first система регулярных возвратов к намерению.

Пользователь задаёт намерение, текст пинга и расписание. DIREM в нужные моменты отправляет сообщения, помогая не потерять выбранный вектор во времени.

DIREM не пытается заменить:

- календарь;
- таск-менеджер;
- будильник;
- habit tracker;
- заметочник;
- AI-ассистента;
- CRM;
- систему проектного управления.

DIREM занимает узкую нишу:

> регулярный личный пинг, привязанный к смыслу, расписанию и состоянию активности.

---

## 2. Цель MVP

Цель MVP — получить рабочий self-hosted Telegram-бот, который позволяет одному пользователю или нескольким пользователям создавать и получать регулярные напоминания.

MVP должен доказать:

1. Telegram-интерфейс удобен для настройки.
2. Reminder-ы корректно сохраняются в БД.
3. Worker надёжно отправляет due reminder-ы.
4. Расписание переживает перезапуск контейнеров.
5. Пользователь видит список, статус и ближайшие срабатывания.
6. Версия и соавторы доступны через команды.

---

## 3. MVP in scope

### 3.1. Telegram bot

Обязательные команды:

- `/start` — регистрация пользователя и короткое объяснение;
- `/help` — список команд;
- `/new` — создание reminder-а;
- `/list` — список reminder-ов;
- `/pause` — пауза reminder-а;
- `/resume` — возобновление reminder-а;
- `/delete` — удаление reminder-а;
- `/timezone` — настройка timezone пользователя;
- `/status` — краткий статус пользователя и системы;
- `/version` — версия приложения;
- `/credits` — соавторы.

### 3.2. User registration

При первом `/start` бот должен создать пользователя в БД.

Минимальные данные пользователя:

- Telegram user id;
- chat id;
- username, если доступен;
- first name, если доступен;
- timezone;
- created_at;
- updated_at.

Timezone по умолчанию может быть `UTC`, но бот должен явно предложить настроить локальную timezone.

### 3.3. Reminder creation

MVP должен поддерживать создание reminder-а через пошаговый Telegram flow.

Минимальные поля:

- title;
- message text;
- schedule type;
- interval minutes или daily time;
- optional active window;
- enabled/disabled;
- next_run_at.

Обязательные schedule types для MVP:

1. interval-based:
   - каждые N минут;
   - пример: каждые 45 минут.

2. daily fixed time:
   - каждый день в HH:MM по timezone пользователя;
   - пример: каждый день в 22:00.

### 3.4. Active window

Reminder может иметь активное окно внутри суток.

Пример:

```text
active_from = 10:00
active_to = 18:00
```

Если active window задан, reminder отправляется только внутри этого окна по timezone пользователя.

Если active window не задан, reminder активен круглые сутки.

Для MVP достаточно одного окна на reminder.

### 3.5. Multiple reminders

MVP должен поддерживать несколько reminder-ов на одного пользователя.

Минимальные операции:

- создать;
- посмотреть список;
- поставить на паузу;
- возобновить;
- удалить.

Редактирование можно вынести в следующую версию, если оно усложняет MVP.

### 3.6. Worker

Worker отвечает за отправку due reminder-ов.

Требования:

- периодически ищет reminder-ы, у которых `next_run_at <= now`;
- отправляет сообщение в Telegram;
- записывает delivery event;
- пересчитывает следующий `next_run_at`;
- не отправляет disabled/paused reminder-ы;
- не отправляет reminder-ы вне active window;
- не должен массово дублировать отправки после перезапуска.

Для MVP допустим простой polling worker.

### 3.7. Delivery log

MVP должен иметь минимальный delivery log.

Минимальные поля события:

- reminder_id;
- user_id;
- scheduled_for;
- sent_at;
- status;
- error message, если отправка не удалась.

Статусы:

- `sent`;
- `failed`;
- `skipped`.

### 3.8. Status screen

Команда `/status` должна показывать:

- timezone пользователя;
- количество active reminder-ов;
- ближайшее срабатывание;
- версию приложения.

Для MVP не требуется показывать системную health-информацию контейнеров.

### 3.9. Versioning

Команда `/version` обязательна в MVP.

Минимальный вывод:

```text
DIREM v0.1.0
Commit: <short sha or unknown>
Build: <date or unknown>
Environment: <local/prod>
DB migration: <revision or unknown>
```

Если commit/build metadata недоступны, бот должен показывать `unknown`, а не падать.

### 3.10. Credits

Команда `/credits` обязательна в MVP.

Минимальный вывод:

```text
Project Owner:
- 1D1L1R

Co-authors:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — implementation executor
```

---

## 4. MVP out of scope

В MVP не входят:

- веб-дашборд;
- Telegram WebApp;
- мобильное приложение;
- десктопное приложение;
- принудительный звук;
- принудительное видео;
- Siren Mode / Anti-Zalip Mode;
- AI-generated reminder messages;
- LLM-интеграция;
- сложные rituals;
- недельные summary;
- аналитика продуктивности;
- календарные интеграции;
- Google Calendar;
- Notion;
- Todoist;
- multi-user teams/workspaces;
- роли и права;
- оплата;
- публичный SaaS;
- админ-панель;
- mascot/stickers/ReMemBear UI;
- импорт старого PHP-кода;
- миграция старой базы ReMemBear.

---

## 5. Допустимый technical scope MVP

MVP может включать только технические части, необходимые для устойчивого self-hosted запуска:

- Docker Compose;
- backend/bot service;
- worker service;
- PostgreSQL;
- migrations;
- `.env.example`;
- README with run instructions;
- базовые tests/smoke checks;
- structured logging.

Не нужно делать production-grade observability в MVP.

Допустимо:

- simple logs to stdout;
- basic error handling;
- simple retry strategy for Telegram send failures.

---

## 6. Пользовательские сценарии MVP

### Scenario 1 — first start

1. Пользователь открывает Telegram bot.
2. Отправляет `/start`.
3. Бот создаёт пользователя.
4. Бот объясняет, что такое DIREM.
5. Бот предлагает настроить timezone.

Acceptance:

- пользователь создан в БД;
- повторный `/start` не создаёт дубликат;
- команда не падает, если username отсутствует.

### Scenario 2 — set timezone

1. Пользователь отправляет `/timezone`.
2. Бот предлагает ввести timezone.
3. Пользователь вводит, например, `Asia/Almaty`.
4. Бот сохраняет timezone.

Acceptance:

- валидная timezone сохраняется;
- невалидная timezone отклоняется с понятным сообщением;
- timezone используется при расчёте daily reminder и active window.

### Scenario 3 — create interval reminder

1. Пользователь отправляет `/new`.
2. Вводит title.
3. Вводит message text.
4. Выбирает interval schedule.
5. Вводит интервал в минутах.
6. Выбирает active window или пропускает.
7. Подтверждает создание.

Acceptance:

- reminder создан;
- `next_run_at` рассчитан;
- reminder виден в `/list`;
- worker отправляет сообщение по расписанию.

### Scenario 4 — create daily reminder

1. Пользователь создаёт reminder.
2. Выбирает daily fixed time.
3. Вводит HH:MM.
4. Подтверждает.

Acceptance:

- next_run_at считается по timezone пользователя;
- если время сегодня уже прошло, next_run_at ставится на следующий день;
- сообщение отправляется в нужное локальное время.

### Scenario 5 — pause and resume

1. Пользователь вызывает `/pause`.
2. Выбирает reminder.
3. Reminder становится paused.
4. Worker его не отправляет.
5. Пользователь вызывает `/resume`.
6. Reminder снова активен.

Acceptance:

- paused reminder не отправляется;
- после resume next_run_at пересчитывается корректно;
- статус виден в `/list`.

### Scenario 6 — delete reminder

1. Пользователь вызывает `/delete`.
2. Выбирает reminder.
3. Бот просит подтвердить.
4. Пользователь подтверждает.
5. Reminder удаляется или soft-deleted.

Acceptance:

- случайное удаление невозможно без подтверждения;
- удалённый reminder не отправляется;
- удалённый reminder не отображается в обычном `/list`.

### Scenario 7 — version and credits

1. Пользователь вызывает `/version`.
2. Бот показывает версию.
3. Пользователь вызывает `/credits`.
4. Бот показывает project owner и co-authors.

Acceptance:

- команды доступны всегда;
- команды не зависят от наличия reminder-ов;
- формат стабилен и читаем.

---

## 7. Data model scope MVP

Минимальные сущности:

### users

- id;
- telegram_user_id;
- chat_id;
- username;
- first_name;
- timezone;
- created_at;
- updated_at.

### reminders

- id;
- user_id;
- title;
- message_text;
- schedule_type;
- interval_minutes;
- daily_time;
- active_from;
- active_to;
- timezone;
- status;
- next_run_at;
- created_at;
- updated_at;
- deleted_at.

### reminder_deliveries

- id;
- reminder_id;
- user_id;
- scheduled_for;
- sent_at;
- status;
- error_message;
- created_at.

### user_states

- id;
- user_id;
- state;
- payload_json;
- created_at;
- updated_at.

---

## 8. Reliability requirements MVP

MVP не обязан быть enterprise-grade, но должен избегать очевидных проблем.

Обязательно:

- no secrets in git;
- `.env.example` only;
- graceful handling of Telegram API errors;
- no duplicate user records for same Telegram id;
- no duplicate send storm after restart;
- migrations are repeatable;
- containers restart cleanly;
- bot can recover from invalid user input.

Желательно:

- idempotent worker claim;
- basic DB indexes for due reminder lookup;
- structured logs.

---

## 9. UX constraints MVP

1. Настройка должна происходить внутри Telegram.
2. Flow не должен требовать длинных инструкций.
3. Бот должен всегда показывать, что именно будет создано перед подтверждением.
4. Ошибки ввода должны быть короткими и понятными.
5. Inline buttons предпочтительнее там, где они уменьшают риск ошибочного ввода.
6. Удаление требует подтверждения.
7. `/help` должен быть достаточно коротким.

---

## 10. Definition of Done for MVP

MVP готов, когда выполнено всё:

- проект запускается через Docker Compose;
- миграции применяются с нуля;
- бот отвечает на `/start`;
- пользователь может настроить timezone;
- пользователь может создать interval reminder;
- пользователь может создать daily reminder;
- пользователь может посмотреть `/list`;
- worker отправляет due reminder;
- delivery event записывается;
- пользователь может pause/resume reminder;
- пользователь может delete reminder;
- `/status` работает;
- `/version` работает;
- `/credits` работает;
- перезапуск контейнеров не ломает расписание;
- секреты не попадают в репозиторий;
- README содержит команды запуска;
- CHANGELOG содержит запись `v0.1.0`;
- smoke-test checklist пройден.

---

## 11. Release target

Первый релиз:

```text
Version: 0.1.0
Git tag: direm-v0.1.0
Release name: Core MVP
```

Релиз должен включать:

- working bot;
- worker;
- DB schema;
- docs baseline;
- smoke tests;
- visible version;
- visible credits.

---

## 12. Scope guard для implementation executor

Текст, который можно вставлять в тикеты для Bushid Ronin V:

```text
You are implementing DIREM MVP.
Use docs/CONCEPT.md and docs/PRODUCT_SCOPE.md as source of truth.
Implement only the current ticket scope.
Do not implement out-of-scope features.
Do not add web dashboard, AI generation, rituals, analytics, or integrations.
Preserve versioning and coauthor metadata.
If a design choice is not specified, choose the simplest implementation that does not block the documented roadmap.
```

---

## 13. Короткий lock

> MVP DIREM должен быть маленьким, устойчивым и полезным.  
> Не расширять его до платформы до тех пор, пока не доказан базовый цикл: создать намерение → получить пинг → управлять расписанием → видеть состояние.

