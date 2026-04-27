# DIREM — Versioning v0.1

## 0. Назначение документа

Этот документ фиксирует правила версионирования DIREM.

Он отвечает на вопросы:

- как формируются версии приложения;
- как называются git tags;
- что должно попадать в `/version`;
- как вести `CHANGELOG.md`;
- как связывать версию кода, миграций и релизов;
- что должен соблюдать implementation при изменениях.

`VERSIONING.md` обязателен для чтения перед релизными и инфраструктурными тикетами.

---

## 1. Versioning model

DIREM использует Semantic Versioning:

```text
MAJOR.MINOR.PATCH
```

Пример:

```text
0.1.0
0.1.1
0.2.0
1.0.0
```

До стабильного публичного релиза проект находится в `0.x`.

---

## 2. Значение частей версии

### MAJOR

Увеличивается при несовместимых изменениях архитектуры, API, данных или пользовательской модели.

Примеры:

- переход с Telegram-only на multi-interface core;
- несовместимая миграция БД;
- изменение модели расписаний, требующее ручной миграции;
- удаление старых команд или сценариев.

До `1.0.0` breaking changes допустимы, но всё равно должны быть описаны в `CHANGELOG.md`.

### MINOR

Увеличивается при добавлении новой функциональности без поломки существующих сценариев.

Примеры:

- добавлены rituals/templates;
- добавлена история ответов;
- добавлен weekly summary;
- добавлен Telegram WebApp dashboard;
- добавлен новый тип расписания.

### PATCH

Увеличивается при исправлениях и малых улучшениях без изменения пользовательской модели.

Примеры:

- bugfix в расчёте `next_run_at`;
- исправление текста команды;
- фиксы миграций без изменения доменной модели;
- улучшение логирования;
- исправление worker retry behavior.

---

## 3. MVP release target

Первый релиз:

```text
Version: 0.1.0
Git tag: direm-v0.1.0
Release name: Core MVP
```

`v0.1.0` считается готовым только если выполнен MVP Definition of Done из `docs/PRODUCT_SCOPE.md`.

---

## 4. Git tag format

Формат тега:

```text
direm-vMAJOR.MINOR.PATCH
```

Примеры:

```text
direm-v0.1.0
direm-v0.1.1
direm-v0.2.0
direm-v1.0.0
```

Не использовать неоднозначные теги:

```text
v1
latest
stable
release
prod
```

---

## 5. Branch naming

Рекомендуемый формат feature branches:

```text
feature/DIREM-XXX-short-name
fix/DIREM-XXX-short-name
docs/DIREM-XXX-short-name
release/direm-vX.Y.Z
```

Примеры:

```text
feature/DIREM-001-project-skeleton
feature/DIREM-006-worker-due-reminders
fix/DIREM-014-next-run-active-window
docs/DIREM-003-versioning
release/direm-v0.1.0
```

---

## 6. Commit style

Жёсткий Conventional Commits не обязателен, но рекомендуемая форма:

```text
DIREM-XXX: short imperative summary
```

Примеры:

```text
DIREM-001: add Python project skeleton
DIREM-004: implement timezone setup flow
DIREM-006: add due reminder worker loop
DIREM-008: add version and credits commands
```

Для мелких docs-only изменений допустимо:

```text
docs: update product scope
chore: update env example
```

---

## 7. Changelog rules

В репозитории должен быть `CHANGELOG.md`.

Формат:

```markdown
# Changelog

## [0.1.0] - YYYY-MM-DD

### Added
- ...

### Changed
- ...

### Fixed
- ...

### Removed
- ...

### Security
- ...
```

Для каждого релиза обязательно:

- версия;
- дата;
- краткое описание изменений;
- breaking changes, если есть;
- migration notes, если есть;
- credits preserved.

---

## 8. Version metadata

DIREM должен уметь показывать версию через команду:

```text
/version
```

Минимальный вывод:

```text
DIREM v0.1.0
Commit: <short sha or unknown>
Build: <date or unknown>
Environment: <local/prod>
DB migration: <revision or unknown>
```

Если metadata недоступна, использовать `unknown`.

Команда `/version` не должна падать из-за отсутствия commit sha, build date или DB revision.

---

## 9. Environment variables for versioning

Рекомендуемые переменные:

```text
DIREM_ENV=local
DIREM_VERSION=0.1.0
DIREM_COMMIT_SHA=unknown
DIREM_BUILD_DATE=unknown
```

В `.env.example` должны быть только безопасные placeholder-значения.

Пример:

```text
DIREM_ENV=local
DIREM_VERSION=0.1.0
DIREM_COMMIT_SHA=unknown
DIREM_BUILD_DATE=unknown
```

---

## 10. Build metadata

Для локального запуска допустимо:

```text
Commit: unknown
Build: unknown
Environment: local
```

Для релизного запуска желательно передавать metadata при build/deploy:

```text
DIREM_VERSION=0.1.0
DIREM_COMMIT_SHA=<git short sha>
DIREM_BUILD_DATE=<ISO timestamp>
DIREM_ENV=prod
```

---

## 11. DB migration version

DIREM использует Alembic.

`/version` должен пытаться показать текущую Alembic revision.

Пример:

```text
DB migration: 20260425_001_initial_schema
```

Если БД недоступна или revision не читается:

```text
DB migration: unknown
```

Это не должно ломать команду `/version`.

---

## 12. Release checklist

Перед созданием git tag нужно проверить:

- `CHANGELOG.md` обновлён;
- версия в env/package metadata обновлена;
- миграции применяются с нуля;
- `/version` показывает ожидаемую версию;
- `/credits` работает;
- smoke checklist из `PRODUCT_SCOPE.md` пройден;
- секреты не попали в git;
- `.env.example` актуален;
- README содержит команды запуска;
- docs не противоречат текущей реализации.

После этого:

```bash
git tag direm-v0.1.0
git push origin direm-v0.1.0
```

---

## 13. Pre-release versions

Если нужно маркировать промежуточные тестовые сборки, использовать suffix только в release notes или build metadata, но не усложнять git tags в MVP.

Допустимо в `/version`:

```text
DIREM v0.1.0-dev
DIREM v0.1.0-rc1
```

Но git tag для финального релиза должен быть чистым:

```text
direm-v0.1.0
```

---

## 14. Version visibility rule

Версия должна быть видима пользователю с первого MVP.

Обязательно:

- команда `/version`;
- версия в README;
- версия в CHANGELOG;
- git tag на релизе.

Желательно:

- версия в startup logs;
- версия в `/status` коротко;
- commit sha в deployment logs.

---

## 15. Coauthor metadata

Информация о соавторстве должна сохраняться независимо от версии.

Минимальные места:

- `docs/COAUTHORS.md`;
- README;
- `/credits`;
- release notes, если уместно.

Implementation не должен удалять или переименовывать coauthor metadata без отдельного тикета.

---

## 16. Legacy note

Старый PHP-прототип не влияет на версию нового DIREM.

`v0.1.0` — это первая версия новой реализации, а не продолжение версии старого ReMemBear.

Если legacy-файлы когда-либо упоминаются, они должны быть обозначены как historical reference only.

---

## 17. Scope guard for implementation

Текст для тикетов:

```text
Follow docs/VERSIONING.md.
Do not remove /version or /credits behavior.
Do not hardcode real build metadata.
Use unknown fallback for missing version metadata.
Use git tag format direm-vX.Y.Z for releases.
Update CHANGELOG.md for user-visible or release-relevant changes.
Do not rename coauthors or remove credits metadata.
```

---

## 18. Короткий lock

> Каждый релиз DIREM должен иметь видимую версию, понятный changelog, стабильный git tag и сохранённые credits.  
> Версия — это не украшение, а способ понимать, какой именно бот сейчас работает.

