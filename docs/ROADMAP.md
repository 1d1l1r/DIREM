# DIREM — Roadmap v0.1

## 0. Назначение документа

Этот документ фиксирует карту развития DIREM.

Он нужен, чтобы:

- отделить MVP от будущих идей;
- не тащить roadmap-фичи в первый релиз;
- дать implementation понятный горизонт развития;
- сохранить продуктовую логику по версиям;
- понимать, какие решения сейчас должны быть простыми, а какие нужно оставить расширяемыми.

Главное правило:

> Roadmap — это направление, а не разрешение реализовывать всё сразу.

Implementation может читать roadmap для контекста, но реализует только активный тикет.

---

## 1. Общая траектория

DIREM развивается поэтапно:

```text
v0.1.0 — Core MVP
v0.2.0 — Reliability & Editing
v0.3.0 — Templates / Rituals
v0.4.0 — History & Reflection
v0.5.0 — Project Pulse
v0.6.0 — Telegram UX polish
v0.7.0 — Optional WebApp dashboard
v1.0.0 — Stable self-hosted release
```

Смысловая траектория:

```text
Reminder bot
→ Intent keeper
→ Ritual engine
→ Reflection/history layer
→ Personal process pulse
```

---

## 2. Version v0.1.0 — Core MVP

### Цель

Получить маленький, устойчивый, self-hosted Telegram bot, который умеет создавать, хранить и отправлять регулярные reminder-ы.

### Основной результат

Пользователь может:

- запустить бота;
- настроить timezone;
- создать interval reminder;
- создать daily reminder;
- увидеть список reminder-ов;
- поставить reminder на паузу;
- возобновить reminder;
- удалить reminder;
- получить scheduled message;
- посмотреть `/version`;
- посмотреть `/credits`.

### In scope

- Python project skeleton;
- Docker Compose;
- PostgreSQL;
- SQLAlchemy models;
- Alembic migrations;
- aiogram bot service;
- worker service;
- users;
- reminders;
- reminder deliveries;
- user states / FSM;
- `/start`;
- `/help`;
- `/new`;
- `/list`;
- `/pause`;
- `/resume`;
- `/delete`;
- `/timezone`;
- `/status`;
- `/version`;
- `/credits`;
- README;
- CHANGELOG;
- smoke checklist.

### Out of scope

- edit reminder flow, если усложняет MVP;
- web dashboard;
- Telegram WebApp;
- rituals/templates;
- AI generation;
- weekly summary;
- integrations;
- public SaaS;
- payment;
- mascot/stickers.

### Release tag

```text
direm-v0.1.0
```

---

## 3. Version v0.2.0 — Reliability & Editing

### Цель

Сделать базовый цикл удобнее и надёжнее после первого MVP.

### Candidate features

- edit reminder flow;
- better `/status`;
- delivery retry policy;
- safer worker claim logic;
- better failed delivery handling;
- improved active window handling;
- optional overnight active windows;
- better validation messages;
- improved `/list` with inline actions;
- simple admin/debug command for owner only;
- tests for services and worker;
- more complete smoke tests.

### Продуктовый смысл

После v0.2.0 DIREM должен ощущаться не как прототип, а как надёжный личный бот, которым можно реально пользоваться каждый день.

### Release tag

```text
direm-v0.2.0
```

---

## 4. Version v0.3.0 — Templates / Rituals

### Цель

Добавить шаблонные сценарии, чтобы пользователь не собирал всё вручную каждый раз.

### Candidate features

- `/templates`;
- morning check template;
- evening reflection template;
- project pulse template;
- focus ping template;
- custom template creation;
- template preview before creation;
- template-based reminder creation.

### Possible built-in templates

```text
Morning Check
- Что сегодня важно удержать?
- Какой один шаг сделает день не пустым?

Evening Reflection
- Что сегодня было сделано?
- Что нужно перенести на завтра?

Project Pulse
- Какой следующий конкретный шаг по проекту?
- Что заблокировано?

Focus Return
- Вернись к текущему вектору.
- Что сейчас должно быть закрыто?
```

### Продуктовый смысл

DIREM начинает быть не просто настройщиком расписаний, а библиотекой полезных ритмов.

### Release tag

```text
direm-v0.3.0
```

---

## 5. Version v0.4.0 — History & Reflection

### Цель

Добавить слой истории: что отправлялось, когда пользователь отвечал, какие процессы реально жили.

### Candidate features

- `/history`;
- reminder delivery timeline;
- user response tracking;
- simple answer capture;
- daily reflection log;
- export to markdown/json;
- view last N events;
- reminder-level history.

### Data expansion

Possible new entities:

```text
reminder_responses
intent_logs
reflection_entries
```

### Продуктовый смысл

DIREM начинает показывать не только будущие пинги, но и след процесса во времени.

### Release tag

```text
direm-v0.4.0
```

---

## 6. Version v0.5.0 — Project Pulse

### Цель

Сделать DIREM полезным для живых проектов: музыкальных, кодовых, учебных, внутренних рабочих.

### Candidate features

- project entity;
- reminder grouping by project;
- project pulse command;
- project status note;
- next action field;
- blocker field;
- lightweight project dashboard inside Telegram;
- weekly project digest.

### Possible commands

```text
/projects
/project_new
/project_status
/project_pulse
/project_archive
```

### Продуктовый смысл

DIREM становится слоем регулярного возвращения не только к одиночным намерениям, но и к долгим проектам.

### Release tag

```text
direm-v0.5.0
```

---

## 7. Version v0.6.0 — Telegram UX Polish

### Цель

Сделать Telegram UX быстрым, чистым и приятным.

### Candidate features

- better inline action menus;
- compact reminder cards;
- pagination for long lists;
- quick actions: pause 1 day / pause until tomorrow / skip next;
- duplicate reminder;
- better confirmation screens;
- better error messages;
- command menu setup;
- owner-only diagnostics;
- optional language strings structure.

### Продуктовый смысл

Снижение трения. Пользователь должен управлять DIREM без ощущения, что он заполняет анкету.

### Release tag

```text
direm-v0.6.0
```

---

## 8. Version v0.7.0 — Optional WebApp Dashboard

### Цель

Добавить визуальный интерфейс только если Telegram-only UX станет тесным.

### Candidate features

- Telegram WebApp or separate web dashboard;
- list reminders;
- edit reminders;
- view history;
- project grouping;
- basic charts;
- import/export;
- owner auth.

### Important lock

Web dashboard не должен появиться раньше, чем Telegram MVP доказал полезность.

Dashboard — не ядро DIREM, а дополнительная поверхность управления.

### Release tag

```text
direm-v0.7.0
```

---

## 9. Version v1.0.0 — Stable self-hosted release

### Цель

Зафиксировать стабильную версию для длительного личного использования.

### Requirements

- stable Docker Compose deployment;
- migration path from previous versions;
- reliable worker;
- no known duplicate-send bugs;
- stable commands;
- stable docs;
- clear backup/restore instructions;
- clear update instructions;
- stable `/version`;
- stable `/credits`;
- documented configuration;
- documented limitations.

### Release tag

```text
direm-v1.0.0
```

---

## 10. Backlog ideas

Эти идеи сохранены, но не входят в ближайший roadmap.

### 10.1. AI-generated messages

Возможность генерировать варианты пингов по tone/profile.

Not now because:

- усложняет систему;
- требует LLM-интеграции;
- может размыть простоту DIREM.

### 10.2. External integrations

Возможные интеграции:

- Google Calendar;
- Notion;
- Todoist;
- GitHub issues;
- local project trackers.

Not now because:

- повышает сложность авторизации;
- расширяет scope;
- превращает DIREM в интеграционный хаб раньше времени.

### 10.3. Team mode

Мультипользовательские пространства, командные ритуалы, общие project pulses.

Not now because:

- DIREM сначала должен доказать одиночный use-case;
- появятся роли, права, приватность, moderation.

### 10.4. Public SaaS

Публичный сервис с регистрацией, оплатой и хостингом для других людей.

Not now because:

- текущий target — self-hosted личный инструмент;
- SaaS потребует security, billing, abuse handling, support.

### 10.5. Mascot / ReMemBear layer

Маскот, стикеры, playful reactions, legacy nods.

Not now because:

- MVP должен ощущаться как инструмент;
- маскот может появиться позже как polish, не как core.

---

## 11. Explicit non-roadmap

Следующие вещи не являются частью roadmap DIREM:

- будильник;
- принудительный звук;
- принудительное видео;
- антисон-сирена;
- desktop alarm companion;
- mobile alarm app;
- health/safety monitoring;
- emergency alert system.

Если такие идеи когда-либо появятся, они должны оформляться как отдельный проект, а не как расширение DIREM Core.

---

## 12. Roadmap guard for implementation

Текст для тикетов:

```text
Read docs/ROADMAP.md only for context.
Do not implement future roadmap features unless this ticket explicitly includes them.
Current roadmap items are not permission to expand scope.
If a future feature seems easy to add now, do not add it without explicit approval.
Prefer simple architecture that does not block roadmap, but do not build roadmap early.
```

---

## 13. Version dependency map

```text
v0.1.0 Core MVP
  required before: everything else

v0.2.0 Reliability & Editing
  depends on: stable reminders, worker, delivery log

v0.3.0 Templates / Rituals
  depends on: stable create/list flows and schedule model

v0.4.0 History & Reflection
  depends on: delivery log and optional response capture

v0.5.0 Project Pulse
  depends on: intents/reminders/history being stable enough

v0.6.0 Telegram UX Polish
  depends on: real use pain points from v0.1-v0.5

v0.7.0 Optional WebApp Dashboard
  depends on: Telegram UX limits becoming obvious

v1.0.0 Stable
  depends on: proven daily use and clean migration path
```

---

## 14. Current priority

Current priority is only:

```text
Ship v0.1.0 Core MVP.
```

Everything else is parked.

---

## 15. Short lock

> DIREM grows from a small reliable reminder core into an intent/ritual/history system only af