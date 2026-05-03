# DIREM — концепт v0.1

## 0. Lock по направлению

DIREM не является будильником, сиреной, антисон-приложением или системой принудительного аудио/видео.  
Модули вроде `Siren Mode`, `Anti-Zalip Mode`, принудительного запуска трека, громкости или видео исключены из текущей концепции.

DIREM — это Telegram-first система для ритмического удержания намерений, фокуса и личных процессов.

Главная идея:

> Пользователь формулирует намерение, а DIREM мягко возвращает его к этому намерению во времени.

Не task manager.  
Не календарь.  
Не будильник.  
Не трекер привычек в лоб.  

DIREM — это слой регулярного возвращения к выбранному вектору.

---

## 1. Что берём из старого ReMemBear

Старый PHP-код не считается технической базой. Он используется только как презентация исходной идеи.

Берём смысл:

- периодические сообщения;
- пользовательский текст напоминания;
- интервал повторения;
- активное временное окно;
- старт/стоп;
- Telegram как основной интерфейс;
- простота настройки без тяжёлого UI.

Не берём:

- текущую структуру кода;
- текущую БД;
- текущую логику cron как архитектурный образец;
- токены, пароли, секреты;
- старую модель “один пользователь = одно напоминание” как финальную модель.

ReMemBear может остаться как legacy/easter egg/маскот в будущем, но не входит в MVP.

---

## 2. Продуктовое определение

**DIREM** — Telegram-бот для настройки и сопровождения регулярных личных пингов, чек-инов и ритуалов, которые помогают удерживать выбранные намерения во времени.

Примеры намерений:

- “каждые 45 минут возвращай меня к фокусу”;
- “по вечерам спрашивай, что сделано по проекту”;
- “раз в день напоминай про важную мысль”;
- “в рабочее время пингуй про конкретную задачу”;
- “каждое утро задавай один и тот же вопрос”;
- “не дай забыть про процесс, пока он активен”.

Ключевое отличие от обычных напоминаний:

> DIREM работает не только с событием, а с длительным состоянием намерения.

---

## 3. Пользовательская модель

### 3.1. Intent

Intent — это смысловой объект: “что я хочу удерживать”.

Примеры:

- “Писать диплом”;
- “Не распыляться по проектам”;
- “Следить за сервером”;
- “Каждый вечер фиксировать прогресс”;
- “Пить воду”;
- “Вернуться к треку”.

### 3.2. Reminder

Reminder — конкретное расписание, привязанное к intent.

У одного intent может быть несколько reminder-ов.

Например:

Intent: “Morning focus”

- будний чек в 11:00;
- вечерний отчёт в 22:00;
- фокус-пинг каждые 60 минут с 13:00 до 18:00.

### 3.3. Ritual

Ritual — шаблонный сценарий, который может состоять из одного или нескольких сообщений.

Примеры:

- утренний чек;
- вечерний отчёт;
- фокус-сессия;
- недельный обзор;
- проектный пульс.

В MVP ritual можно не реализовывать как отдельную сущность, но архитектурно оставить место.

---

## 4. Базовые сценарии MVP

### 4.1. Создать регулярный пинг

Пользователь:

1. Нажимает `/new`.
2. Вводит название.
3. Вводит текст сообщения.
4. Выбирает интервал или фиксированное время.
5. Выбирает активное окно, если нужно.
6. Подтверждает запуск.

Бот:

- создаёт intent/reminder;
- показывает краткое резюме;
- начинает отправлять сообщения по расписанию.

### 4.2. Посмотреть активные пинги

Команда:

- `/list`

Показывает:

- название;
- статус;
- следующее срабатывание;
- интервал/время;
- активное окно.

### 4.3. Пауза/возобновление

Команды:

- `/pause`
- `/resume`

Через inline-кнопки пользователь выбирает конкретный reminder.

### 4.4. Редактирование

Команда:

- `/edit`

Поля:

- название;
- текст;
- расписание;
- активное окно;
- timezone;
- enabled/disabled.

### 4.5. Удаление

Команда:

- `/delete`

С обязательным подтверждением.

### 4.6. Статус системы

Команда:

- `/status`

Показывает:

- сколько active reminders;
- ближайшие срабатывания;
- timezone пользователя;
- состояние worker-а, если доступно;
- версию приложения.

### 4.7. Версия и соавторы

Команды:

- `/version`
- `/credits`

`/version` показывает:

- semantic version;
- git commit;
- build date;
- environment;
- migration version.

`/credits` показывает:

- Project Owner: 1D1L1R;
- Rein Hard V — architecture, scope lock, review;
- Bushid Ronin V — implementation executor.

---

## 5. Тон и UX

DIREM должен ощущаться как инструмент, а не как игрушка.

Тон:

- короткий;
- ясный;
- без канцелярита;
- без чрезмерной “милоты”;
- дружелюбный, но не сюсюкающий;
- с уважением к вниманию пользователя.

Пример хорошего сообщения:

> Фокус: утренний настрой
> Вернись к текущему шагу. Что должно быть закрыто следующим действием?

Пример плохого сообщения:

> Приветик! Не забудь быть продуктивным! Ты справишься!

---

## 6. Команды MVP

Минимальный набор:

- `/start` — вход и короткое описание;
- `/help` — список команд;
- `/new` — создать reminder;
- `/list` — список reminder-ов;
- `/edit` — изменить reminder;
- `/pause` — поставить на паузу;
- `/resume` — возобновить;
- `/delete` — удалить;
- `/status` — состояние;
- `/timezone` — настройка timezone;
- `/version` — версия;
- `/credits` — соавторы.

Возможные будущие:

- `/templates`;
- `/history`;
- `/export`;
- `/weekly`;
- `/settings`.

---

## 7. Версионирование

DIREM использует semantic versioning:

- `0.1.0` — первый рабочий MVP;
- `0.2.0` — multi-reminder stable;
- `0.3.0` — templates/rituals;
- `0.4.0` — history/reflection;
- `1.0.0` — стабильный self-hosted релиз.

Git tags:

- `direm-v0.1.0`
- `direm-v0.2.0`
- `direm-v0.3.0`

Каждый релиз должен иметь:

- `CHANGELOG.md` entry;
- migration version;
- smoke-test checklist;
- credits preserved.

---

## 8. Соавторство

Базовая модель:

```text
Project Owner:
- 1D1L1R

Co-authors:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — implementation executor
```

Эта информация должна быть отражена:

- в `README.md`;
- в `docs/COAUTHORS.md`;
- в `/credits` внутри Telegram-бота;
- при желании — в release notes.

---

## 9. Архитектурные принципы

1. **Telegram-first, но не Telegram-locked**  
   Telegram — основной интерфейс, но доменная логика не должна жить внутри Telegram handlers.

2. **UTC внутри, локальное время на границе**  
   Все `next_run_at`, события и логи хранятся в UTC. Timezone используется при вводе/выводе и расчёте локальных окон.

3. **Reminder как доменная сущность**  
   Не “команда отправляет сообщение”, а “worker исполняет due reminder”.

4. **Worker не должен дублировать отправки**  
   Нужны блокировки, статусы попыток или транзакционный claim due jobs.

5. **Версия видима пользователю**  
   `/version` обязателен с первой версии.

6. **Секреты не попадают в git**  
   Только `.env.example`, реальные значения — вне репозитория.

7. **Старый PHP не мигрируется**  
   Он не является legacy codebase. Это historical prototype.

---

## 10. Предварительная дорожная карта

### v0.1.0 — Core MVP

Цель: рабочий Telegram bot с несколькими reminder-ами, расписанием и worker-ом.

Фичи:

- project skeleton;
- Telegram bot startup;
- user registration on `/start`;
- timezone setting;
- create/list/pause/resume/delete reminder;
- interval-based schedule;
- fixed-time daily schedule;
- active time window;
- worker sends due reminders;
- `/version`;
- `/credits`;
- docs baseline.

### v0.2.0 — Editing & Reliability

Фичи:

- edit flows;
- delivery log;
- retry policy;
- anti-duplicate protection;
- better status screen;
- smoke tests;
- DB migrations stabilized.

### v0.3.0 — Templates / Rituals

Фичи:

- built-in templates;
- morning check;
- evening reflection;
- project pulse;
- simple response tracking.

### v0.4.0 — History & Review

Фичи:

- reminder history;
- user responses;
- weekly summary;
- export.

---

## 11. Out of scope для MVP

Не делаем в MVP:

- веб-дашборд;
- мобильное приложение;
- десктопную сирену;
- принудительный звук/видео;
- AI-generated messages;
- сложную аналитику;
- командные пространства;
- оплату;
- публичный SaaS;
- интеграции с календарём;
- ReMemBear mascot/stickers.

---

## 12. Первый набор документов в репозитории

```text
docs/
  CONCEPT.md
  PRODUCT_SCOPE.md
  ARCHITECTURE.md
  VERSIONING.md
  COAUTHORS.md
  ROADMAP.md
  DECISIONS.md
  tickets/
    DIREM-001-project-skeleton.md
    DIREM-002-domain-model.md
    DIREM-003-telegram-start-help.md
    DIREM-004-user-timezone.md
    DIREM-005-create-reminder-flow.md
    DIREM-006-worker-due-reminders.md
    DIREM-007-list-pause-resume-delete.md
    DIREM-008-version-credits.md
    DIREM-009-smoke-tests.md
```

---

## 13. MVP acceptance

MVP считается живым, если можно:

1. Запустить проект через Docker Compose.
2. Написать боту `/start`.
3. Настроить timezone.
4. Создать reminder с текстом и интервалом.
5. Увидеть его в `/list`.
6. Получить сообщение в заданное время.
7. Поставить reminder на паузу.
8. Возобновить reminder.
9. Удалить reminder.
10. Проверить `/version`.
11. Проверить `/credits`.
12. Убедиться, что после перезапуска контейнеров расписание сохраняется.

---

## 14. Короткая формула проекта

> DIREM — это не будильник и не таск-менеджер.  
> Это Telegram-first движок регулярных возвратов к намерению.

---

## 15. Handoff для Bushid Ronin V

### 15.1. Что передавать implementation

Bushid Ronin V нужно передавать **и Markdown-документы, и тикеты**.

Но с жёсткой иерархией:

```text
Docs = конституция проекта
Tickets = конкретный приказ на спринт
Code = результат исполнения
```

Рекомендуемый handoff-пакет для каждого спринта:

```text
docs/CONCEPT.md
docs/PRODUCT_SCOPE.md
docs/ARCHITECTURE.md
docs/VERSIONING.md
docs/COAUTHORS.md
docs/ROADMAP.md
docs/DECISIONS.md
docs/tickets/DIREM-XXX-*.md
```

Тикет должен быть главным рабочим документом, но он обязан ссылаться на relevant docs.

Пример:

```text
Source of truth:
- docs/CONCEPT.md
- docs/ARCHITECTURE.md
- docs/VERSIONING.md

Implement only the scope described in this ticket.
Do not expand scope based on roadmap sections unless explicitly requested.
```

### 15.2. Как ограничивать scope

 На один заход ему лучше давать:

1. Общие docs проекта.
2. Один конкретный тикет или маленький batch тикетов.
3. Явный запрет реализовывать будущие roadmap-фичи.
4. Acceptance checklist.
5. Expected files changed / allowed areas.

Формула:

```text
Read the project docs for context.
Implement only ticket DIREM-XXX.
Do not implement future roadmap items.
Do not refactor unrelated areas.
Preserve versioning and coauthor metadata.
```

### 15.3. Что делать со старым PHP

Старые файлы `ReMemBear.php` и `CronBear.php` не должны передаваться как техническая база для продолжения разработки.

Правильная схема:

1. **Основной источник правды** — Markdown-документы и тикеты новой версии DIREM.
2. **Старые PHP-файлы** — только historical reference, если нужно понять исходный пользовательский сценарий.
3. **Raw legacy files не использовать напрямую** в реализации.
4. **Секреты из старых файлов считаются скомпрометированными** и не должны попадать в репозиторий, тикеты или промпты.
5. Если legacy-код всё же хранится в репе, он должен быть:
   - очищен от токенов, паролей и host/user данных;
   - положен в `legacy/` или `docs/legacy/`;
   - помечен как `reference-only`;
   - исключён из runtime и production path.

Рекомендуемый формат Ronin:

```text
Use docs/CONCEPT.md, docs/PRODUCT_SCOPE.md, docs/ARCHITECTURE.md and docs/tickets/*.md as source of truth.
Implement only the active ticket scope.
Do not port legacy PHP code.
Legacy ReMemBear/CronBear files are historical references only.
Implement DIREM from scratch according to the tickets and architecture docs.
```

