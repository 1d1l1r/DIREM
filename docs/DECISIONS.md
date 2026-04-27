# DIREM — Decisions v0.1

## 0. Назначение документа

Этот документ фиксирует ключевые архитектурные и продуктовые решения DIREM в формате lightweight ADR.

ADR = Architecture Decision Record.

Цель:

- сохранить, почему были выбраны конкретные решения;
- не возвращаться к одним и тем же развилкам без причины;
- дать implementation понятные constraints;
- отделить принятые решения от будущих идей;
- упростить ревью и поддержку проекта.

Каждое решение имеет статус.

Возможные статусы:

```text
Accepted
Proposed
Deprecated
Superseded
Rejected
```

---

## ADR-001 — Use Python 3.12 + aiogram 3

Status: Accepted

### Context

DIREM — Telegram-first бот с пошаговыми пользовательскими flows, командами, inline-кнопками и будущими сценариями вроде templates/rituals.

Нужен стек, который хорошо подходит для Telegram bot development, worker-логики, расписаний и self-hosted запуска.

### Decision

Использовать:

```text
Python 3.12
aiogram 3
```

### Rationale

Python хорошо подходит для:

- Telegram bot flows;
- scheduler/worker logic;
- быстрых MVP;
- чистого разделения services/domain;
- тестов через pytest.

aiogram 3 выбран потому что:

- хорошо работает с Telegram Bot API;
- поддерживает routers;
- поддерживает FSM flows;
- подходит для async-архитектуры;
- распространён и понятен для implementation.

### Consequences

Плюсы:

- быстрый старт;
- простой bot/worker split;
- нормальная работа с async Telegram API;
- хорошая совместимость с SQLAlchemy 2 async.

Минусы:

- нужно аккуратно не смешивать handlers и business logic;
- async-код требует дисциплины;
- часть логики нужно явно тестировать, чтобы не утонуть в flows.

---

## ADR-002 — Use PostgreSQL + SQLAlchemy 2 + Alembic

Status: Accepted

### Context

DIREM должен хранить пользователей, reminders, delivery log, user states и будущую историю.

SQLite мог бы подойти для совсем маленького прототипа, но проект планируется как self-hosted сервис с Docker Compose и будущими расширениями.

### Decision

Использовать:

```text
PostgreSQL
SQLAlchemy 2.x
Alembic
```

### Rationale

PostgreSQL выбран потому что:

- устойчив для self-hosted сервиса;
- хорошо работает с timestamps/timezones;
- поддерживает транзакции и row-level locking;
- подходит для worker claim logic;
- расширяем под будущую history/reflection модель.

SQLAlchemy 2 выбран как основной ORM.

Alembic выбран для миграций схемы.

### Consequences

Плюсы:

- нормальная миграционная история;
- удобная работа с моделями;
- проще избежать дублей в worker-е;
- легче масштабировать data model.

Минусы:

- больше инфраструктуры, чем SQLite;
- нужен отдельный db service;
- локальный запуск требует Docker Compose или установленный PostgreSQL.

---

## ADR-003 — Split bot service and worker service

Status: Accepted

### Context

DIREM имеет два разных типа нагрузки:

1. Telegram interaction: commands, callbacks, user flows.
2. Scheduled execution: due reminders, delivery log, next_run_at recalculation.

Если смешать всё в одном процессе, будет проще стартовать, но сложнее поддерживать и тестировать.

### Decision

Разделить runtime на два сервиса:

```text
bot service
worker service
```

Оба сервиса используют один кодовый образ, но разные entrypoint commands.

### Rationale

Bot service должен отвечать только за Telegram interface.

Worker service должен отвечать только за scheduled reminder execution.

Так проще:

- тестировать worker отдельно;
- перезапускать bot без нарушения расписаний;
- перезапускать worker без влияния на Telegram flows;
- позже добавить queue/retry logic;
- сохранить чистую архитектуру.

### Consequences

Плюсы:

- чистое разделение ответственности;
- меньше риска засунуть scheduler в Telegram handlers;
- проще будущая production hardening.

Минусы:

- в Docker Compose появляется второй service;
- нужно следить, чтобы worker не запускался в нескольких экземплярах без claim protection;
- больше дисциплины в shared services.

---

## ADR-004 — Store timestamps in UTC, interpret user schedules via IANA timezones

Status: Accepted

### Context

Пользователь задаёт расписание в локальном времени.

Например:

```text
каждый день в 22:00 Asia/Almaty
```

Но worker должен стабильно сравнивать due reminder-ы независимо от локальных зон.

### Decision

Хранить timestamps в UTC.

Использовать IANA timezone strings для пользовательских расписаний.

Пример:

```text
Asia/Almaty
Europe/Moscow
UTC
```

### Rationale

UTC внутри снижает риск ошибок при сравнении времени.

IANA timezone лучше, чем ручной offset, потому что:

- понятнее пользователю;
- стандартнее;
- переносимо;
- не ломает будущие timezone cases.

### Consequences

Плюсы:

- worker logic проще;
- daily reminders считаются корректнее;
- active windows можно интерпретировать в timezone пользователя;
- меньше хака с ручными offset-ами.

Минусы:

- нужно валидировать timezone;
- schedule calculation требует аккуратных unit tests;
- локальное время должно конвертироваться только на границах.

---

## ADR-005 — Use polling mode for MVP

Status: Accepted

### Context

Telegram bot может работать через polling или webhook.

Webhook требует публичный HTTPS endpoint, reverse proxy, сертификаты и сетевую настройку.

DIREM MVP ориентирован на простой self-hosted запуск.

### Decision

Для MVP использовать Telegram polling mode.

Webhook оставить на будущее.

### Rationale

Polling проще для:

- локальной разработки;
- Docker Compose запуска;
- домашнего сервера;
- отладки;
- первого MVP.

### Consequences

Плюсы:

- не нужен публичный endpoint;
- не нужен Caddy/Nginx для старта;
- проще smoke testing;
- меньше инфраструктурного шума.

Минусы:

- polling менее красив для production deployment;
- один активный bot polling process должен быть основным;
- webhook всё равно может понадобиться позже.

---

## ADR-006 — Keep Telegram-first MVP, no web dashboard

Status: Accepted

### Context

У DIREM может появиться WebApp или dashboard, но MVP должен проверить базовый цикл:

```text
создать intention/reminder → получить ping → управлять расписанием → видеть состояние
```

Если делать dashboard сразу, проект расползётся.

### Decision

MVP остаётся Telegram-first.

Не делать в MVP:

- web dashboard;
- Telegram WebApp;
- admin panel;
- charts;
- visual analytics.

### Rationale

Telegram уже является интерфейсом, где пользователь получает reminder-ы.

Значит настройка в Telegram уменьшает product surface и ускоряет MVP.

### Consequences

Плюсы:

- меньше scope;
- быстрее релиз;
- меньше frontend-инфраструктуры;
- проще для self-hosted запуска.

Минусы:

- сложные настройки могут быть менее удобными;
- длинные списки reminder-ов могут стать неудобными;
- позже может понадобиться WebApp.

---

## ADR-007 — Do not port legacy PHP code

Status: Accepted

### Context

Старый ReMemBear/CronBear PHP-код является историческим прототипом идеи.

Он показывает, что пользователь хотел:

- периодические сообщения;
- интервал;
- активное окно;
- старт/стоп;
- Telegram interface.

Но старый код не должен определять новую архитектуру.

### Decision

Не портировать старый PHP-код.

Не использовать старую структуру БД как обязательную основу.

Не переносить старые секреты, токены, пароли или host/user данные.

### Rationale

Старый код полезен как историческая заметка, но не как foundation.

Новый DIREM строится с нуля по:

- `docs/CONCEPT.md`;
- `docs/PRODUCT_SCOPE.md`;
- `docs/ARCHITECTURE.md`;
- `docs/VERSIONING.md`;
- `docs/COAUTHORS.md`;
- активным тикетам.

### Consequences

Плюсы:

- не наследуем технический долг;
- не тянем секреты;
- не копируем старые cron/timezone хаки;
- можем нормально построить domain model.

Минусы:

- часть поведения нужно заново описывать;
- нельзя быстро “допилить старое”;
- MVP требует project skeleton с нуля.

---

## ADR-008 — Use docs and tickets as source of truth for implementation

Status: Accepted

### Context

DIREM будет реализовываться через implementation.

Чтобы implementation не расползался по roadmap и не импровизировал, нужна иерархия источников правды.

### Decision

Использовать иерархию:

```text
Project Owner decision > active ticket > docs > existing code > assumptions
```

Практическая формула:

```text
Docs = конституция проекта
Tickets = конкретный приказ на спринт
Code = результат исполнения
```

### Rationale

Docs фиксируют долгую форму проекта.

Tickets фиксируют конкретный scope работы.

Implementation должен читать docs, но реализовывать только активный тикет.

### Consequences

Плюсы:

- меньше scope creep;
- проще ревью;
- легче держать roadmap отдельно от MVP;
- понятнее, что делать при конфликте.

Минусы:

- нужно поддерживать docs актуальными;
- тикеты должны быть достаточно конкретными;
- при противоречиях нужно явно обновлять документы.

---

## ADR-009 — Keep version and credits visible from MVP

Status: Accepted

### Context

Для DIREM важно понимать, какая версия бота сейчас работает, и сохранять видимое соавторство.

Версия нужна для debugging, releases и deployment sanity.

Credits нужны как часть проектной модели.

### Decision

С первого MVP обязательны команды:

```text
/version
/credits
```

`/version` показывает:

```text
DIREM vX.Y.Z
Commit
Build
Environment
DB migration
```

`/credits` показывает:

```text
Project Owner: 1D1L1R
Co-authors: Rein Hard V, Bushid Ronin V
```

### Rationale

Версия — это не украшение, а способ понимать, какой именно бот работает.

Credits — не случайный текст, а часть проектной идентичности.

### Consequences

Плюсы:

- проще debug;
- проще release tracking;
- coauthor metadata не теряется;
- implementation получает стабильный acceptance item.

Минусы:

- нужно хранить metadata централизованно;
- нужно обновлять CHANGELOG/version при релизах;
- tests должны проверять credits/version output.

---

## ADR-010 — MVP excludes alarm/siren/anti-zalip features

Status: Accepted

### Context

В обсуждении возникали идеи про принудительный звук, видео, сирену и anti-zalip режимы.

Такие функции относятся к будильникам, desktop/mobile alarm companions или safety tools, а не к DIREM Core.

### Decision

Исключить из DIREM MVP и roadmap Core:

- Siren Mode;
- Anti-Zalip Mode;
- принудительный звук;
- принудительное видео;
- desktop alarm companion;
- mobile alarm app;
- health/safety monitoring;
- emergency alert system.

### Rationale

DIREM не будильник.

DIREM — система регулярных возвратов к намерению.

Принудительный звук/видео потребуют отдельной нативной архитектуры и размоют продукт.

### Consequences

Плюсы:

- сохраняем чистый продуктовый фокус;
- не лезем в платформенные ограничения Telegram;
- не превращаем MVP в safety/alarm system.

Минусы:

- Telegram-бот не сможет гарантировать привлечение внимания;
- пользователь зависит от уведомлений Telegram;
- отдельный alarm-проект возможен только вне DIREM Core.

---

## ADR-011 — Use simple polling worker, no external queue in MVP

Status: Accepted

### Context

Для отправки reminder-ов нужен scheduler/worker.

Можно использовать Celery, Redis, external queue или полноценный scheduler framework.

Но MVP должен быть маленьким и self-hosted.

### Decision

Использовать простой polling worker поверх PostgreSQL.

Не добавлять Redis/Celery/external queue в MVP.

### Rationale

PostgreSQL уже хранит reminders и `next_run_at`.

Простой worker достаточно хорош для MVP:

```text
loop → claim due reminders → send → log → update next_run_at → sleep
```

### Consequences

Плюсы:

- меньше инфраструктуры;
- проще Docker Compose;
- проще отладка;
- меньше moving parts.

Минусы:

- нужно аккуратно реализовать claim/dedup;
- сложные retry/delay стратегии придётся добавить позже;
- масштабирование worker-а пока ограничено.

---

## ADR-012 — Reject overnight active windows in MVP

Status: Accepted

### Context

Active window может быть дневным:

```text
10:00–18:00
```

Или overnight:

```text
22:00–04:00
```

Overnight windows усложняют schedule calculation.

### Decision

В MVP поддерживать только окна, где:

```text
active_from < active_to
```

Если пользователь вводит overnight window, бот должен дать понятное сообщение, что такие окна пока не поддерживаются.

### Rationale

MVP должен проверить базовый цикл, а не все edge cases времени.

Overnight можно добавить в v0.2.0 или позже.

### Consequences

Плюсы:

- проще schedule logic;
- меньше багов;
- проще unit tests;
- проще UX.

Минусы:

- нельзя задать ночные окна в MVP;
- некоторым сценариям понадобится workaround.

---

## ADR-013 — Avoid catch-up storms after downtime

Status: Accepted

### Context

Если worker был выключен несколько часов, interval reminder мог “пропустить” много срабатываний.

Плохой вариант — после старта отправить все пропущенные сообщения подряд.

### Decision

MVP не делает catch-up storm.

Правило:

```text
Send at most one message per due reminder per worker tick, then move next_run_at to the next valid future time.
```

Для interval reminders после успешной отправки использовать:

```text
next_run_at = now + interval_minutes
```

с учётом active window.

### Rationale

DIREM должен мягко возвращать к намерению, а не спамить пачкой старых пингов.

### Consequences

Плюсы:

- нет message storm после downtime;
- поведение понятнее пользователю;
- worker проще.

Минусы:

- пропущенные reminders не воспроизводятся;
- delivery history покажет только фактические отправки/failed/skipped события.

---

## ADR-014 — Keep MVP single-user friendly but multi-user capable

Status: Accepted

### Context

DIREM в первую очередь создаётся как личный self-hosted инструмент.

Но Telegram bot технически может использоваться несколькими пользователями.

### Decision

MVP должен быть multi-user capable на уровне data model:

- users table;
- reminders привязаны к user_id;
- deliveries привязаны к user_id;
- timezone per user.

Но не делать team/workspace features.

### Rationale

Это почти не усложняет базовую модель, но предотвращает тупик.

### Consequences

Плюсы:

- можно безопасно дать бота нескольким людям;
- будущие team features не требуют полной переделки;
- reminders изолированы по пользователям.

Минусы:

- нужно не забывать фильтровать данные по user_id;
- команды list/pause/delete должны показывать только reminders текущего пользователя.

---

## ADR-015 — Keep mascot/ReMemBear out of MVP UI

Status: Accepted

### Context

ReMemBear может быть симпатичным legacy/easter egg/маскотом, но DIREM MVP должен ощущаться как инструмент.

### Decision

Не использовать ReMemBear mascot/stickers/playful UI в MVP.

Можно оставить ReMemBear только как historical note в docs, если нужно.

### Rationale

MVP должен быть ясным, коротким и функциональным.

Маскот может появиться позже как polish, но не должен определять продуктовый тон.

### Consequences

Плюсы:

- DIREM выглядит серьёзнее;
- меньше отвлечения от core loop;
- проще Telegram UX.

Минусы:

- меньше playful identity на старте;
- legacy-символика откладывается.

---

## 16. Decision index

```text
ADR-001 Accepted — Use Python 3.12 + aiogram 3
ADR-002 Accepted — Use PostgreSQL + SQLAlchemy 2 + Alembic
ADR-003 Accepted — Split bot service and worker service
ADR-004 Accepted — Store timestamps in UTC, interpret user schedules via IANA timezones
ADR-005 Accepted — Use polling mode for MVP
ADR-006 Accepted — Keep Telegram-first MVP, no web dashboard
ADR-007 Accepted — Do not port legacy PHP code
ADR-008 Accepted — Use docs and tickets as source of truth for implementation
ADR-009 Accepted — Keep version and credits visible from MVP
ADR-010 Accepted — MVP excludes alarm/siren/anti-zalip features
ADR-011 Accepted — Use simple polling worker, no external queue in MVP
ADR-012 Accepted — Reject overnight active windows in MVP
ADR-013 Accepted — Avoid catch-up storms after downtime
ADR-014 Accepted — Keep MVP single-user friendly but multi-user capable
ADR-015 Accepted — Keep mascot/ReMemBear out of MVP UI
```

---

## 17. Scope guard for implementation

Text for tickets:

```text
Follow docs/DECISIONS.md.
Do not reverse accepted ADRs inside an implementation ticket.
If implementation reveals that an ADR is wrong or too restrictive, stop and propose an ADR update instead of silently changing architecture.
Do not add Redis/Celery/web dashboard/webhook mode/AI generation unless explicitly requested by an active ticket.
Keep the MVP small and aligned with accepted decisions.
```

---

## 18. Short lock

> DIREM decisions are intentionally boring: small stack, clear services, UTC time, visible versions, no legacy port, no sirens, no dashboard in MVP.  
> The goal is not to impress the architecture gods.  
> The goal is to ship a reliable intent-reminder core without losing the shape of the project.

