# Модуль 2.1 — Ветки и слияние

> **Контекст модуля:** Проект `devtool` развивается, и появляется первая параллельная задача — добавить анализ частоты символов. В реальной команде никто не пишет новый код прямо в `main` — для каждой задачи создаётся отдельная ветка. В этом модуле ты научишься работать с ветками, сливать их обратно в `main` и разрешать конфликты когда два человека (или ты в двух ветках) изменили одно и то же место.

**Что ты сделаешь в этом модуле:**
- Создашь ветку для новой фичи и поработаешь в ней
- Сымитируешь параллельную работу: изменения идут одновременно в двух ветках
- Сольёшь ветку в `main` через `git merge`
- Намеренно создашь конфликт и разрешишь его вручную
- Научишься читать граф истории

---

## Задача 1. Создаём ветку для новой фичи

### Контекст

Тебе поставили задачу: добавить в `devtool` анализ частоты символов. Это самостоятельная фича — она не должна ломать `main` пока разрабатывается. Создаёшь ветку, работаешь в ней изолированно.

### Задание

1. Убедись что находишься в ветке `main` и `git status` чистый.
2. Создай ветку `feature/char-frequency` и сразу переключись на неё.
3. Создай новый файл `analyzer.py` с содержимым:

```python
def char_frequency(filepath):
    """Возвращает словарь с частотой каждого символа в файле."""
    freq = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            for char in line:
                freq[char] = freq.get(char, 0) + 1
    return freq
```

4. Закоммить файл с осмысленным сообщением.
5. Добавь ещё один коммит в эту ветку — добавь функцию `top_chars` в тот же `analyzer.py`:

```python
def top_chars(filepath, n=5):
    """Возвращает n самых частых символов."""
    freq = char_frequency(filepath)
    return sorted(freq.items(), key=lambda x: x[1], reverse=True)[:n]
```

6. Проверь через `git log --oneline` что в ветке два новых коммита.

### Подсказка

```
git status
git checkout -b feature/char-frequency
# или современный синтаксис:
git switch -c feature/char-frequency
git add analyzer.py
git commit -m "..."
git log --oneline
```

### Проверка

`git log --oneline` в ветке `feature/char-frequency` покажет два новых коммита поверх истории `main`:

```
c3d4e5f Add top_chars function to analyzer
b2c3d4e Add char_frequency function
a1b2c3d Add count_chars function     ← последний коммит из main
...
```

`git branch` покажет список веток, текущая отмечена `*`:

```
* feature/char-frequency
  main
```

### Разбор

```bash
git status        # убеждаемся что всё чисто
git branch        # смотрим что мы на main

# Создаём ветку и сразу переключаемся
git switch -c feature/char-frequency
# эквивалент старого: git checkout -b feature/char-frequency

# Создаём analyzer.py (содержимое выше)
git add analyzer.py
git commit -m "Add char_frequency function"

# Добавляем top_chars в тот же файл
git add analyzer.py
git commit -m "Add top_chars function to analyzer"

git log --oneline   # два новых коммита в ветке
```

**Что такое ветка на самом деле?** Это просто указатель на коммит. Когда ты делаешь `git switch -c feature/char-frequency` — Git создаёт новый указатель на текущий коммит. Каждый новый коммит двигает этот указатель вперёд. Ветка `main` при этом остаётся стоять на месте — она не знает про твои новые коммиты.

---

### ⚠️ Частые ошибки

**Ошибка 1: Создал ветку но не переключился на неё**

`git branch feature/char-frequency` создаёт ветку, но не переключает. Коммиты уйдут в `main`. Всегда используй `git switch -c` или `git checkout -b` — они делают оба действия сразу. Проверь текущую ветку:

```bash
git branch        # звёздочка показывает где ты
git status        # первая строка: "On branch ..."
```

**Ошибка 2: `git switch` не найдена**

Команда `git switch` появилась в Git 2.23. Проверь версию:

```bash
git --version
```

Если версия старше — используй `git checkout -b feature/char-frequency`. Обе команды делают одно и то же.

---

## Задача 2. Параллельная работа: изменения в `main`

### Контекст

Пока ты разрабатываешь фичу в своей ветке, кто-то (или ты сам по другой задаче) вносит изменения в `main`. Так работают все команды. Сымитируем это: переключимся на `main` и сделаем там коммит.

### Задание

1. Переключись обратно на ветку `main`.
2. Убедись что `analyzer.py` здесь нет — ветки изолированы.
3. Исправь баг в `main.py`: функция `count_lines` считает пустые строки, добавим фильтрацию:

```python
def count_lines(filepath):
    """Возвращает количество непустых строк в файле."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return sum(1 for line in f if line.strip())
```

4. Закоммить исправление в `main`.
5. Посмотри граф истории — обе ветки должны видеть расхождение:

```bash
git log --graph --oneline --all
```

### Подсказка

```
git switch main
ls                      # проверить что analyzer.py отсутствует
git add main.py
git commit -m "..."
git log --graph --oneline --all
```

### Проверка

`git log --graph --oneline --all` покажет граф с расхождением:

```
* d4e5f6g Fix count_lines to skip empty lines    ← main
| * c3d4e5f Add top_chars function                ← feature/char-frequency
| * b2c3d4e Add char_frequency function
|/
* a1b2c3d Add count_chars function               ← общий предок
```

Видишь `|/` — здесь ветки разошлись. Это нормально, именно для этого ветки и нужны.

### Разбор

```bash
git switch main
# Git мгновенно переключает рабочую директорию —
# analyzer.py исчезает, потому что его нет в main

ls          # analyzer.py отсутствует — это правильно

# Редактируем main.py (содержимое выше)
git add main.py
git commit -m "Fix count_lines to skip empty lines"

# Смотрим граф всех веток
git log --graph --oneline --all
```

**Флаги `git log`:**
- `--graph` — рисует ASCII-граф слева
- `--oneline` — компактный формат: хэш + сообщение
- `--all` — показывает все ветки, не только текущую

> 💡 Удобный алиас — можно добавить в глобальный конфиг и вызывать как `git lg`:
> ```bash
> git config --global alias.lg "log --graph --oneline --all"
> ```

---

### ⚠️ Частые ошибки

**Ошибка 1: Переключился на `main` но забыл закоммитить изменения в фича-ветке**

Git не даст переключиться если есть несохранённые изменения — предупредит об ошибке. Либо закоммить, либо спрятать через `git stash` (тема следующих модулей).

```
error: Your local changes to the following files would be overwritten by checkout
```

Решение: закоммить или `git stash` перед переключением.

**Ошибка 2: `--all` не показывает фича-ветку**

Убедись что хотя бы один коммит в ветке сделан. Просто созданная но пустая ветка в `--all` не отображается отдельно.

---

## Задача 3. Слияние: `git merge`

### Контекст

Фича готова, баг в `main` исправлен. Пора соединить работу: влить `feature/char-frequency` обратно в `main`. Это делается через `git merge` — находясь в `main`, ты говоришь "возьми все коммиты из той ветки и добавь их сюда".

### Задание

1. Убедись что ты на ветке `main`.
2. Слей ветку `feature/char-frequency` в `main`.
3. Изучи результат — Git сообщит о типе слияния.
4. Посмотри граф истории после слияния.
5. Убедись что `analyzer.py` теперь есть в `main`.

### Подсказка

```
git switch main
git merge feature/char-frequency
git log --graph --oneline --all
ls
```

### Проверка

После слияния `git log --graph --oneline --all` покажет merge commit:

```
*   e5f6g7h Merge branch 'feature/char-frequency'
|\
| * c3d4e5f Add top_chars function
| * b2c3d4e Add char_frequency function
* | d4e5f6g Fix count_lines to skip empty lines
|/
* a1b2c3d Add count_chars function
```

`ls` покажет `analyzer.py` — он теперь в `main`. Функции из обеих веток объединены.

### Разбор

```bash
git switch main

# Сливаем feature-ветку в main
git merge feature/char-frequency
# Git создаст "merge commit" — специальный коммит с двумя родителями
# Сообщение предложит автоматически: "Merge branch 'feature/char-frequency'"
# Откроется редактор — можно оставить как есть, сохранить и закрыть

git log --graph --oneline --all
# Видим ромбовидную структуру — ветки разошлись и снова сошлись

ls      # analyzer.py появился в main
cat analyzer.py   # функции на месте
```

**Два типа merge:**

`Fast-forward` — если `main` не двигался пока разрабатывалась фича, Git просто передвигает указатель `main` вперёд без создания merge commit. Граф остаётся линейным.

`Merge commit` (наш случай) — если обе ветки двигались независимо, Git создаёт новый коммит с двумя родителями. В графе появляется ромб.

> 💡 **После слияния** фича-ветку принято удалять — она выполнила свою функцию:
> ```bash
> git branch -d feature/char-frequency
> ```

---

### ⚠️ Частые ошибки

**Ошибка 1: Открылся редактор для сообщения merge commit и непонятно как выйти**

По умолчанию открывается `vim`. Чтобы сохранить и выйти: нажми `Esc`, затем введи `:wq` и `Enter`.

Если хочешь сменить редактор на что-то понятнее:

```bash
git config --global core.editor "nano"   # nano проще для новичков
```

**Ошибка 2: Случайно сделал merge не из той ветки**

Отмени merge, пока не было новых коммитов:

```bash
git merge --abort   # если merge ещё не завершён (был конфликт)
# или если merge завершён:
git reset --hard HEAD~1   # откатить последний коммит (merge commit)
```

---

## Задача 4. Конфликт: создаём и разрешаем

### Контекст

Конфликт возникает когда две ветки изменили **одно и то же место** в файле. Git не знает какую версию оставить — и просит тебя решить. Это не катастрофа, это штатная ситуация. Сейчас намеренно создадим конфликт и разберёмся как его разрешать.

### Задание

1. Создай новую ветку `feature/output-format` от `main` и переключись на неё.
2. В этой ветке измени блок `if __name__ == '__main__':` в `main.py` — добавь форматированный вывод:

```python
if __name__ == '__main__':
    import sys
    filepath = sys.argv[1]
    print(f"Lines:  {count_lines(filepath)}")
    print(f"Words:  {count_words(filepath)}")
```

3. Закоммить изменение.
4. Переключись на `main`.
5. В `main` измени **тот же блок** иначе — добавь JSON-вывод:

```python
if __name__ == '__main__':
    import sys
    import json
    filepath = sys.argv[1]
    result = {"lines": count_lines(filepath), "words": count_words(filepath)}
    print(json.dumps(result))
```

6. Закоммить изменение в `main`.
7. Попробуй слить `feature/output-format` в `main` — получи конфликт.
8. Изучи файл с конфликтными маркерами.
9. Разреши конфликт вручную — оставь форматированный вывод (из фича-ветки), но добавь JSON как опцию через аргумент. Или просто выбери одну версию — главное пройти процесс разрешения.
10. Завершить merge.

### Подсказка

```
git switch -c feature/output-format
# редактируем main.py
git add main.py && git commit -m "..."

git switch main
# редактируем main.py иначе
git add main.py && git commit -m "..."

git merge feature/output-format
# получаем конфликт — читаем вывод Git

# открываем main.py, ищем маркеры <<<<<, =====, >>>>>
# правим файл, убираем маркеры
git add main.py
git commit
```

### Проверка

При попытке merge Git выведет:

```
Auto-merging main.py
CONFLICT (content): Merge conflict in main.py
Automatic merge failed; fix conflicts and then commit the result.
```

`git status` во время конфликта покажет:

```
Unmerged paths:
  (use "git add <file>..." to mark resolution)
        both modified:   main.py
```

После разрешения и `git add main.py` — `git status` покажет:

```
All conflicts fixed but you are still merging.
  (use "git commit" to conclude merge)
```

### Разбор

```bash
git switch -c feature/output-format

# Редактируем блок if __name__ в main.py (форматированный вывод)
git add main.py
git commit -m "Add formatted output to CLI"

git switch main

# Редактируем тот же блок иначе (JSON-вывод)
git add main.py
git commit -m "Add JSON output to CLI"

git merge feature/output-format
# CONFLICT — Git остановился, ждёт решения
```

Открываем `main.py` — видим маркеры конфликта:

```python
if __name__ == '__main__':
    import sys
<<<<<<< HEAD
    import json
    filepath = sys.argv[1]
    result = {"lines": count_lines(filepath), "words": count_words(filepath)}
    print(json.dumps(result))
=======
    filepath = sys.argv[1]
    print(f"Lines:  {count_lines(filepath)}")
    print(f"Words:  {count_words(filepath)}")
>>>>>>> feature/output-format
```

**Как читать маркеры:**
- `<<<<<<< HEAD` — начало версии из текущей ветки (`main`)
- `=======` — разделитель
- `>>>>>>> feature/output-format` — конец версии из сливаемой ветки

Редактируем файл — убираем маркеры, оставляем нужный код (или объединяем оба варианта):

```python
if __name__ == '__main__':
    import sys
    filepath = sys.argv[1]
    print(f"Lines:  {count_lines(filepath)}")
    print(f"Words:  {count_words(filepath)}")
```

```bash
# Сохраняем файл, маркеров больше нет

git add main.py                    # помечаем конфликт как разрешённый
git commit                         # завершаем merge (сообщение предложит автоматически)

git log --graph --oneline --all    # видим ромб — merge завершён
```

> 💡 **Редакторы с поддержкой конфликтов:** VS Code подсвечивает конфликтные маркеры и показывает кнопки "Accept Current / Accept Incoming / Accept Both". Это удобнее чем редактировать текст вручную.

---

### ⚠️ Частые ошибки

**Ошибка 1: Закоммитил файл с маркерами конфликта внутри**

Случается когда торопишься — маркеры `<<<<<<<` остаются в коде. Исправь:

```bash
# открой файл, найди и удали все строки с <<<<<<<, =======, >>>>>>>
git add main.py
git commit --amend   # перезапишет последний коммит
```

**Ошибка 2: Хочу отменить merge и вернуться к состоянию до него**

```bash
git merge --abort   # работает пока merge не завершён (есть конфликты)
```

Если merge уже завершён (нечаянно сделал коммит):

```bash
git reset --hard HEAD~1   # откатить merge commit — осторожно, необратимо
```

---

## 🏁 Финальная задача — всё вместе

### Контекст

Весь модуль в одном сценарии: новая фича в ветке, параллельные изменения в `main`, слияние с конфликтом.

### Задание

1. От текущего `main` создай ветку `feature/stats-report`.
2. В этой ветке добавь в `main.py` функцию `full_report`:

```python
def full_report(filepath):
    """Возвращает полную статистику по файлу."""
    return {
        "lines": count_lines(filepath),
        "words": count_words(filepath),
        "chars": count_chars(filepath),
    }
```

3. Закоммить в ветке.
4. Переключись на `main`, добавь в начало `main.py` строку-заголовок:

```python
# devtool: text file analysis utility
```

5. Закоммить в `main`.
6. Вернись в `feature/stats-report`, добавь **туда же** в начало `main.py` другую строку:

```python
# devtool v1.0 — analyze text files
```

7. Закоммить.
8. Переключись на `main`, слей `feature/stats-report` — получи конфликт в первой строке.
9. Разреши конфликт: оставь строку `# devtool: text file analysis utility` из `main`.
10. Завершить merge.
11. Посмотри финальный граф: `git log --graph --oneline --all`.

### Ожидаемый граф

```
*   Merge branch 'feature/stats-report'
|\
| * Add version comment to main.py
| * Add full_report function
* | Add description comment to main.py
|/
*   Merge branch 'feature/output-format'
...
```

---

## Итоги модуля

Ты освоил:

| Команда | Что делает |
|---|---|
| `git switch -c <branch>` | Создать ветку и переключиться на неё |
| `git switch <branch>` | Переключиться на существующую ветку |
| `git branch` | Показать список веток |
| `git branch -d <branch>` | Удалить ветку (после слияния) |
| `git merge <branch>` | Слить указанную ветку в текущую |
| `git merge --abort` | Отменить merge при конфликте |
| `git log --graph --oneline --all` | Граф истории всех веток |

**Главная идея модуля:** ветка — это изолированное пространство для работы. `main` всегда остаётся стабильным. Конфликты при слиянии — не ошибка системы, а штатная ситуация: Git честно говорит "не знаю что оставить, реши сам". Умение читать маркеры конфликта и разрешать их — базовый навык любого разработчика.

---

> **Следующий модуль:** 2.2 — Rebase и чистая история. Узнаешь как переписать историю ветки, склеить черновые коммиты в один и понять когда `rebase` лучше `merge`.
