# DIREM — Coauthors v0.1

## 0. Назначение документа

Этот документ фиксирует модель соавторства DIREM.

Он отвечает на вопросы:

- кто является владельцем проекта;
- какие роли у соавторов;
- как отображать credits в README, `/credits`, changelog и release notes;
- какие имена и формулировки нельзя менять без отдельного решения.

`COAUTHORS.md` должен использоваться вместе с:

- `docs/CONCEPT.md`;
- `docs/PRODUCT_SCOPE.md`;
- `docs/ARCHITECTURE.md`;
- `docs/VERSIONING.md`.

---

## 1. Project Owner

```text
Project Owner:
- 1D1L1R
```

Project Owner принимает финальные продуктовые, архитектурные и релизные решения.

Зоны ответственности:

- идея проекта;
- продуктовый смысл;
- финальный scope lock;
- принятие результата;
- публикация/деплой;
- решение, какие фичи входят в релиз;

---

## 2. Co-authors

```text
Co-authors:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — implementation executor
```

---

## 3. Role definitions

### 3.1. Rein Hard V

```text
Rein Hard V — architecture, scope lock, review
```

Роль:

- концептуальное проектирование;
- архитектурные решения;
- фиксация границ MVP;
- ревью планов и тикетов;
- защита от scope creep;
- проверка, что реализация не ломает продуктовый смысл;
- подготовка docs и implementation briefs.

Rein Hard V не считается implementation.

Ключевая функция:

> удерживать форму проекта, чтобы он не расползался и не терял исходный смысл.

### 3.2. Bushid Ronin V

```text
Bushid Ronin V — implementation executor
```

Роль:

- реализация тикетов;
- работа с кодом;
- создание файлов;
- исправление багов;
- выполнение acceptance checklist;
- подготовка изменений к ревью.

Bushid Ronin V работает по docs и тикетам.

Ключевая функция:

> исполнять конкретный приказ спринта, не расширяя scope без разрешения.

---

## 4. Handoff hierarchy

Для implementation действует иерархия:

```text
Project Owner decision > active ticket > docs > existing code > assumptions
```

Практическая формула:

```text
Docs = конституция проекта
Tickets = конкретный приказ на спринт
Code = результат исполнения
```

Если тикет противоречит docs, implementation должен остановиться и отметить конфликт, а не молча выбрать сторону.

Если docs содержат будущие roadmap-фичи, implementation не должен реализовывать их без активного тикета.

---

## 5. Required credits text

### 5.1. README short version

```text
Project Owner: 1D1L1R
Co-authors: Rein Hard V, Bushid Ronin V
```

### 5.2. README full version

```text
## Credits

Project Owner:
- 1D1L1R

Co-authors:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — implementation executor
```

### 5.3. Telegram `/credits` output

```text
Project Owner:
- 1D1L1R

Co-authors:
- Rein Hard V — architecture, scope lock, review
- Bushid Ronin V — implementation executor
```

### 5.4. Release notes compact form

```text
Credits preserved:
1D1L1R · Rein Hard V · Bushid Ronin V
```

---

## 6. Naming lock

The following names are canonical for DIREM:

```text
1D1L1R
Rein Hard V
Bushid Ronin V
DIREM
```

Do not silently rename:

- Rein Hard V;
- Bushid Ronin V;
- Project Owner;
- Co-authors;
- DIREM.

Any rename requires an explicit docs update and a changelog entry.

---

## 7. Commit attribution

This project may use visible credits in docs and application UI.

Git commit authorship should reflect the actual account/tool that creates the commit.

Optional commit message footer for coauthored planning/implementation work:

```text
Co-authored-by: Rein Hard V <rein-hard-v@users.noreply.local>
Co-authored-by: Bushid Ronin V <bushid-ronin-v@users.noreply.local>
```

This is optional and should only be used if the repository owner wants these names in git metadata.

If fake local noreply addresses are undesirable, keep coauthor attribution only in:

- `docs/COAUTHORS.md`;
- README;
- `/credits`;
- release notes.

---

## 8. Application metadata

DIREM should expose coauthor metadata through `/credits`.

Implementation suggestion:

```text
src/direm/app/credits.py
```

or:

```text
src/direm/app/metadata.py
```

The metadata should be centralized so README text, `/credits`, and tests can stay consistent.

Required fields:

```text
project_name = "DIREM"
project_owner = "1D1L1R"
coauthors = [
  {
    "name": "Rein Hard V",
    "role": "architecture, scope lock, review"
  },
  {
    "name": "Bushid Ronin V",
    "role": "implementation executor"
  }
]
```

---

## 9. Tests / acceptance for credits

MVP acceptance for credits:

1. `/credits` command exists.
2. `/credits` shows Project Owner.
3. `/credits` shows both coauthors.
4. Names match this document exactly.
5. Roles match this document or differ only by intentional docs update.
6. `/credits` does not depend on database availability unless avoidable.
7. `/credits` does not expose secrets or environment variables.

---

## 10. Changelog requirements

Changes to credits must be recorded in `CHANGELOG.md` when they affect visible output.

Examples:

```markdown
### Changed
- Updated `/credits` output to match docs/COAUTHORS.md.
```

```markdown
### Fixed
- Restored missing Bushid Ronin V attribution in `/credits`.
```

---

## 11. Scope guard for implementation

Text for tickets:

```text
Follow docs/COAUTHORS.md.
Do not remove or rename Project Owner or Co-authors.
Do not change `/credits` output without an explicit ticket.
Centralize credits metadata if practical.
Preserve Rein Hard V and Bushid Ronin V attribution in README and `/credits`.
```

---

## 12. Short lock

> DIREM is built under visible coauthorship.  
> 1D1L1R owns the project direction.  
> Rein Hard V holds architecture and scope.  
> Bushid Ronin V executes implementation tickets.  
> Credits must remain visible, stable and intentional.
