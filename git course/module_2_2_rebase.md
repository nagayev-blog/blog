---
title: "Модуль 2.2 — Rebase и чистая история"
description: "Переносишь коммиты поверх main и склеиваешь черновики в один чистый коммит через rebase и rebase -i"
date: "2026-03-24"
tags: ["dev", "git"]
---

# Модуль 2.2 — Rebase и чистая история

> **Контекст модуля:** Ты умеешь работать с ветками и делать merge. Но у merge есть побочный эффект — история обрастает merge commit'ами и выглядит как паутина. `rebase` — альтернативный способ интегрировать изменения: он переносит коммиты ветки поверх другой, сохраняя линейную историю. В этом модуле разберёшься когда использовать rebase вместо merge, как чистить черновые коммиты через `rebase -i` и почему rebase нельзя применять к публичным веткам.

**Что ты сделаешь в этом модуле:**
- Добавишь фичу несколькими черновыми коммитами, как это бывает в реальной работе
- Перенесёшь ветку поверх обновлённого `main` через `git rebase`
- Склеишь черновые коммиты в один через `git rebase -i`
- Сравнишь граф истории до и после rebase
- Поймёшь золотое правило: rebase только для локальных веток

---

## Задача 1. Создаём ветку с несколькими черновыми коммитами

### Контекст

В реальной работе над фичей коммиты часто выглядят так: "wip", "fix typo", "fix again", "ок теперь точно работает". Это нормальный рабочий процесс — но такую историю стыдно отправлять в `main`. Сначала создадим именно такую "грязную" историю, а потом приберём её.

### Задание

1. Убедись что ты на ветке `main` и история чистая.
2. Создай ветку `feature/cli-args` и переключись на неё.
3. Сделай **четыре** коммита в этой ветке — по одному небольшому изменению, имитируя черновую работу:

   **Коммит 1** — добавь импорт `argparse` в начало `main.py`:
   ```python
   import argparse
   ```

   **Коммит 2** — добавь функцию создания парсера после импорта:
   ```python
   def build_parser():
       parser = argparse.ArgumentParser(description='Analyze text files')
       parser.add_argument('filepath', help='Path to the file')
       return parser
   ```

   **Коммит 3** — добавь аргумент `--lines` в парсер (редактируй `build_parser`):
   ```python
   def build_parser():
       parser = argparse.ArgumentParser(description='Analyze text files')
       parser.add_argument('filepath', help='Path to the file')
       parser.add_argument('--lines', action='store_true', help='Count lines')
       return parser
   ```

   **Коммит 4** — добавь аргумент `--words` в парсер:
   ```python
   def build_parser():
       parser = argparse.ArgumentParser(description='Analyze text files')
       parser.add_argument('filepath', help='Path to the file')
       parser.add_argument('--lines', action='store_true', help='Count lines')
       parser.add_argument('--words', action='store_true', help='Count words')
       return parser
   ```

4. Посмотри историю ветки через `git log --oneline`.

### Подсказка

```bash
git switch -c feature/cli-args
# редактируем main.py, затем:
git add main.py && git commit -m "wip: add argparse import"
# следующее изменение:
git add main.py && git commit -m "wip: add build_parser function"
# и так далее
git log --oneline
```

### Проверка

`git log --oneline` в ветке покажет 4 новых коммита поверх `main`:

```
d4e5f6g wip: add --words argument
c3d4e5f wip: add --lines argument
b2c3d4e wip: add build_parser function
a1b2c3d wip: add argparse import
...   ← коммиты из main
```

### Разбор

```bash
git switch -c feature/cli-args

# Коммит 1
# добавляем import argparse в main.py
git add main.py
git commit -m "wip: add argparse import"

# Коммит 2
# добавляем build_parser()
git add main.py
git commit -m "wip: add build_parser function"

# Коммит 3
# добавляем --lines в build_parser
git add main.py
git commit -m "wip: add --lines argument"

# Коммит 4
# добавляем --words в build_parser
git add main.py
git commit -m "wip: add --words argument"

git log --oneline   # 4 черновых коммита
```

**Зачем намеренно делать "грязные" коммиты?** Это честное отражение реального процесса разработки — думаешь, пробуешь, ошибаешься, правишь. Фиксировать каждый шаг через коммит — хорошая привычка во время работы. Привести в порядок — перед тем как отдать в `main`.

---

### ⚠️ Частые ошибки

**Ошибка 1: Сделал все изменения сразу и закоммитил одним коммитом**

Для этого задания важно именно 4 отдельных коммита — `rebase -i` в следующих задачах будет работать с ними. Если уже закоммитил одним — сбрось и повтори:

```bash
git reset HEAD~1        # отменить последний коммит, изменения останутся
# теперь раздели изменения на части через git add -p
```

**Ошибка 2: Перепутал ветку — коммиты ушли в `main`**

```bash
git log --oneline       # проверить где коммиты
git branch              # проверить текущую ветку
```

Если коммиты в `main` — откати их и перенеси в нужную ветку (это нетривиально, лучше спроси ментора). Проще начать заново с правильной ветки.

---

## Задача 2. Обновляем `main` и применяем `git rebase`

### Контекст

Пока ты работал над `feature/cli-args`, в `main` появились новые коммиты (другой разработчик что-то исправил). Теперь твоя ветка "отстала" от `main`. Вместо merge — применишь rebase: Git возьмёт твои коммиты и "переложит" их поверх актуального `main`, как будто ты начал работу сегодня, а не неделю назад.

### Задание

1. Переключись на `main`.
2. Сделай два новых коммита в `main` (симуляция работы коллеги):

   **Коммит 1** — добавь в `README.md` раздел про установку:
   ```markdown
   ## Установка
   pip install -r requirements.txt
   ```

   **Коммит 2** — добавь в `README.md` раздел про запуск:
   ```markdown
   ## Запуск
   python main.py <filepath>
   ```

3. Посмотри граф — ветки разошлись: `git log --graph --oneline --all`.
4. Переключись обратно на `feature/cli-args`.
5. Выполни `git rebase main` — наблюдай как Git переносит коммиты.
6. Посмотри граф снова — история стала линейной.

### Подсказка

```bash
git switch main
# редактируем README.md, два коммита
git log --graph --oneline --all   # видим расхождение

git switch feature/cli-args
git rebase main
git log --graph --oneline --all   # видим линейную историю
```

### Проверка

**До rebase** граф показывает расхождение:

```
* f6g7h8i Update README: add run instructions    ← main
* e5f6g7h Update README: add install section
| * d4e5f6g wip: add --words argument            ← feature/cli-args
| * c3d4e5f wip: add --lines argument
| * b2c3d4e wip: add build_parser function
| * a1b2c3d wip: add argparse import
|/
* 9h8i7j6k ...                                   ← общий предок
```

**После rebase** история линейная — коммиты фича-ветки перенесены поверх `main`:

```
* d'4e5f6g wip: add --words argument             ← feature/cli-args (новые хэши!)
* c'3d4e5f wip: add --lines argument
* b'2c3d4e wip: add build_parser function
* a'1b2c3d wip: add argparse import
* f6g7h8i Update README: add run instructions    ← бывший верхний коммит main
* e5f6g7h Update README: add install section
* ...
```

Обрати внимание: **хэши коммитов изменились** (обозначены `'`). Rebase создаёт новые коммиты — это важно понять перед следующей задачей.

### Разбор

```bash
git switch main

# Редактируем README.md — добавляем раздел установки
git add README.md
git commit -m "Update README: add install section"

# Редактируем README.md — добавляем раздел запуска
git add README.md
git commit -m "Update README: add run instructions"

git log --graph --oneline --all   # ветки разошлись — видим Y-образный граф

git switch feature/cli-args

git rebase main
# Git делает следующее:
# 1. Находит общего предка feature/cli-args и main
# 2. Сохраняет твои коммиты во временное место
# 3. Переключает ветку на актуальный main
# 4. Последовательно применяет твои коммиты один за другим поверх

git log --graph --oneline --all   # линейная история
```

**Rebase vs Merge — в чём разница:**

| | `merge` | `rebase` |
|---|---|---|
| История | Ромбовидная, с merge commit | Линейная, без лишних коммитов |
| Хэши коммитов | Не меняются | Меняются (новые коммиты) |
| Безопасность | Всегда безопасен | Опасен для публичных веток |
| Читаемость | Сложнее при большом числе веток | Проще — одна линия |

---

### ⚠️ Частые ошибки

**Ошибка 1: Конфликт во время rebase**

Если твои коммиты затрагивают те же места что и новые коммиты `main` — будет конфликт. Git остановится и сообщит:

```
CONFLICT (content): Merge conflict in main.py
error: could not apply a1b2c3d... wip: add argparse import
```

Разрешай так же как при merge — найди маркеры, исправь файл, затем:

```bash
git add main.py
git rebase --continue   # продолжить rebase (не git commit!)
# или отменить всё:
git rebase --abort
```

**Ошибка 2: Сделал rebase на публичной ветке и сломал коллегам историю**

Если ветка уже запушена и кто-то её получил — rebase изменит хэши коммитов, и у коллеги возникнет рассинхронизация. **Золотое правило: rebase только для локальных, ещё не запушенных веток.** Для публичных — только merge.

---

## Задача 3. Интерактивный rebase: склеиваем черновые коммиты

### Контекст

Четыре черновых коммита с "wip:" — это внутренняя кухня, которую незачем показывать в истории `main`. Через `git rebase -i` можно переписать историю ветки: склеить коммиты, переименовать, поменять местами или удалить. Это как редактор истории — прямо перед финальным слиянием.

### Задание

1. Убедись что ты на ветке `feature/cli-args` после rebase из предыдущей задачи.
2. Запусти интерактивный rebase для последних 4 коммитов:
   ```bash
   git rebase -i HEAD~4
   ```
3. Откроется редактор со списком коммитов. Оставь первый как `pick`, остальные три замени на `squash` (или `s`).
4. Сохрани и закрой — откроется второй экран для сообщения итогового коммита.
5. Напиши осмысленное сообщение: `"Add argparse CLI interface with --lines and --words flags"`.
6. Сохрани и закрой.
7. Проверь результат через `git log --oneline` — вместо 4 коммитов должен быть один.

### Подсказка

```bash
git rebase -i HEAD~4
# в редакторе меняем pick → s (squash) для коммитов 2, 3, 4
# первый оставляем pick
# сохраняем, закрываем
# во втором экране пишем финальное сообщение
git log --oneline
```

### Проверка

До `rebase -i`:
```
d4e5f6g wip: add --words argument
c3d4e5f wip: add --lines argument
b2c3d4e wip: add build_parser function
a1b2c3d wip: add argparse import
```

После `rebase -i`:
```
e5f6g7h Add argparse CLI interface with --lines and --words flags
```

Один чистый коммит вместо четырёх черновых. Именно такой коммит приятно видеть в истории `main`.

### Разбор

```bash
git rebase -i HEAD~4
```

Откроется редактор с таким содержимым (коммиты в хронологическом порядке — старые сверху):

```
pick a1b2c3d wip: add argparse import
pick b2c3d4e wip: add build_parser function
pick c3d4e5f wip: add --lines argument
pick d4e5f6g wip: add --words argument

# Rebase ... onto ...
#
# Commands:
# p, pick   = use commit
# s, squash = use commit, but meld into previous commit
# r, reword = use commit, but edit the commit message
# d, drop   = remove commit
```

Редактируем — первый `pick` оставляем, остальные меняем на `s`:

```
pick a1b2c3d wip: add argparse import
s b2c3d4e wip: add build_parser function
s c3d4e5f wip: add --lines argument
s d4e5f6g wip: add --words argument
```

Сохраняем и закрываем (`Esc` → `:wq` в vim, или `Ctrl+X` → `Y` в nano).

Откроется второй экран — редактор сообщения итогового коммита. Удаляем все "wip:" строки, пишем одно осмысленное:

```
Add argparse CLI interface with --lines and --words flags
```

Сохраняем и закрываем.

```bash
git log --oneline   # один чистый коммит
git diff main       # все изменения на месте — только история стала чище
```

**Другие полезные команды в `rebase -i`:**
- `r` (reword) — оставить коммит, но переименовать
- `d` (drop) — удалить коммит полностью
- Поменять строки местами — Git применит коммиты в новом порядке

---

### ⚠️ Частые ошибки

**Ошибка 1: Поставил `squash` на первый коммит**

`squash` означает "склеить с предыдущим". У первого коммита нет предыдущего — Git выдаст ошибку. Первый коммит всегда должен быть `pick`.

```
error: cannot 'squash' without a previous commit
```

Решение: `git rebase --abort`, начать заново с правильной разметкой.

**Ошибка 2: Закрыл редактор сообщения не сохранив — итоговое сообщение некрасивое**

Ничего страшного, можно исправить сразу после:

```bash
git commit --amend   # открывает редактор для последнего коммита
```

---

## Задача 4. Сравниваем графы и обсуждаем когда что использовать

### Контекст

Ветка `feature/cli-args` готова: история чистая, один осмысленный коммит. Сравним два способа интегрировать её в `main` — merge и rebase — и разберёмся когда каждый уместен.

### Задание

1. Переключись на `main`.
2. Слей `feature/cli-args` в `main` через обычный merge:
   ```bash
   git merge feature/cli-args -m "Merge feature/cli-args into main"
   ```
3. Посмотри итоговый граф: `git log --graph --oneline --all`.
4. Сравни с графом который был бы если бы ты не делал rebase перед merge (ромбовидный с 4 черновыми коммитами).
5. Удали фича-ветку: `git branch -d feature/cli-args`.

### Подсказка

```bash
git switch main
git merge feature/cli-args -m "Merge feature/cli-args into main"
git log --graph --oneline --all
git branch -d feature/cli-args
```

### Проверка

Граф после merge будет чистым — один коммит фичи, один merge commit:

```
*   h8i9j0k Merge feature/cli-args into main
|\
| * e5f6g7h Add argparse CLI interface with --lines and --words flags
|/
* f6g7h8i Update README: add run instructions
* e5f6g7h Update README: add install section
* ...
```

Сравни с тем что было бы без `rebase -i` — четыре "wip:" коммита в ромбе. Разница очевидна.

### Разбор

```bash
git switch main
git merge feature/cli-args -m "Merge feature/cli-args into main"
git log --graph --oneline --all

git branch -d feature/cli-args   # ветка выполнила задачу — удаляем
```

**Когда merge, когда rebase — простое правило:**

| Ситуация | Что делать |
|---|---|
| Обновить локальную фича-ветку до актуального `main` | `git rebase main` в фича-ветке |
| Почистить черновые коммиты перед слиянием | `git rebase -i HEAD~N` |
| Влить фича-ветку в `main` | `git merge` из `main` |
| Ветка уже запушена на GitHub | Только `merge`, никакого rebase |
| `main` или другая публичная ветка | Никогда не делать rebase |

**Главное правило rebase:** переписывай только то, что ещё не видели другие. Как только коммиты попали на удалённый сервер и кто-то их получил — они "публичные", трогать нельзя.

---

### ⚠️ Частые ошибки

**Ошибка 1: Сделал `git rebase main` находясь в `main`**

Rebase `main` на себя — бессмысленная операция, но Git выполнит её без ошибки (`Current branch main is up to date`). Убедись что ты в фича-ветке перед rebase:

```bash
git branch   # проверить где ты
```

**Ошибка 2: Удалил ветку до слияния**

```bash
git branch -d feature/cli-args
# error: The branch 'feature/cli-args' is not fully merged.
```

Git защищает от случайного удаления. Если ветка действительно не нужна — используй `-D` (принудительно). Если нужна — сначала слей в `main`.

---

## 🏁 Финальная задача — всё вместе

### Контекст

Полный цикл: черновая разработка → rebase на актуальный main → чистка истории → слияние.

### Задание

1. Создай ветку `feature/report-output` от текущего `main`.
2. Сделай **три** черновых коммита в ветке:
   - Добавь функцию `format_report(stats)` в `main.py`, которая принимает словарь и возвращает отформатированную строку
   - Исправь опечатку в комментарии (имитация мелкой правки)
   - Добавь пустую строку между функциями (имитация форматирования)
3. Переключись на `main`, добавь один коммит (например, добавь строку в `README.md`).
4. Переключись на `feature/report-output`, сделай `git rebase main` — перенеси ветку поверх.
5. Через `git rebase -i HEAD~3` склей три коммита в один с осмысленным сообщением.
6. Переключись на `main`, слей ветку через merge.
7. Удали фича-ветку.
8. Посмотри финальный граф — история должна быть чистой и линейной с одним merge commit.

### Ожидаемый результат

```bash
$ git log --graph --oneline
*   Merge feature/report-output into main
|\
| * Add format_report function to main.py
|/
* Update README: add usage examples
* Merge feature/cli-args into main
...
```

---

## Итоги модуля

Ты освоил:

| Команда | Что делает |
|---|---|
| `git rebase main` | Перенести коммиты текущей ветки поверх `main` |
| `git rebase -i HEAD~N` | Интерактивный rebase последних N коммитов |
| `git rebase --continue` | Продолжить rebase после разрешения конфликта |
| `git rebase --abort` | Отменить rebase и вернуться к исходному состоянию |
| `git commit --amend` | Исправить последний коммит (сообщение или содержимое) |

**Главная идея модуля:** rebase — инструмент для поддержания чистой читаемой истории. `git rebase main` держит фича-ветку актуальной без лишних merge commit'ов. `git rebase -i` позволяет превратить черновые коммиты в один осмысленный перед слиянием. И главное — rebase переписывает историю, поэтому применять его можно только к локальным веткам, которые ещё не видели другие разработчики.

---

> **Следующий модуль:** 3.1 — Первый remote. Подключишь репозиторий к GitHub, научишься делать push/pull и разберёшься в чём разница между `origin/main` и локальным `main`.
