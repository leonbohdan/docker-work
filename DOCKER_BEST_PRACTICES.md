# 🛡️ Docker Rules & Best Practices Guide
### 🇺🇦 Золоті Правила та Найкращі Практики Docker | 🇬🇧 Golden Rules & Best Practices for Docker

Цей документ містить 10 ключових правил з прикладами (❌ Як робити не треба vs ✅ Як робити правильно) як українською, так і англійською мовами, а також важливі додаткові правила безпеки та оптимізації.

---

## 📑 Зміст / Table of Contents
1. [Правило 01: Використовуйте офіційні образи / Rule 01: Use Official Images](#-правило-01-використовуйте-офіційні-образи--rule-01-use-official-images)
2. [Правило 02: Ніколи не використовуйте tag :latest у продакшні / Rule 02: Don't ever use tag :latest in production](#-правило-02-ніколи-не-використовуйте-tag-latest-у-продакшні--rule-02-dont-ever-use-tag-latest-in-production)
3. [Правило 03: Використовуйте найменші базові образи / Rule 03: Use smallest possible base image](#-правило-03-використовуйте-найменші-базові-образи--rule-03-use-smallest-possible-base-image)
4. [Правило 04: Не встановлюйте зайвих пакетів / Rule 04: Don't install unnecessary packages](#-правило-04-не-встановлюйте-зайвих-пакетів--rule-04-dont-install-unnecessary-packages)
5. [Правило 05: Використовуйте багатоетапні збірки / Rule 05: Use multi-stage builds](#-правило-05-використовуйте-багатоетапні-збірки--rule-05-use-multi-stage-builds)
6. [Правило 06: Один контейнер = один застосунок / Rule 06: Each container should run only one application](#-правило-06-один-контейнер--один-застосунок--rule-06-each-container-should-run-only-one-application)
7. [Правило 07: Кешування шарів (від стабільних до динамічних) / Rule 07: Use Layer Caching properly](#-правило-07-кешування-шарів-від-стабільних-до-динамічних--rule-07-use-layer-caching-properly)
8. [Правило 08: Розбивайте довгі RUN команди на кілька рядків / Rule 08: Split long RUN commands](#-правило-08-розбивайте-довгі-run-команди-на-кілька-рядків--rule-08-split-long-run-commands)
9. [Правило 09: Віддавайте перевагу COPY над ADD / Rule 09: Prefer COPY over ADD](#-правило-09-віддавайте-перевагу-copy-над-add--rule-09-prefer-copy-over-add)
10. [Правило 10: ЗАВЖДИ використовуйте WORKDIR / Rule 10: ALWAYS use WORKDIR](#-правило-10-завжди-використовуйте-workdir--rule-10-always-use-workdir)
11. [⭐ Додаткові важливі правила / Bonus Critical Rules](#-додаткові-важливі-правила--bonus-critical-rules)

---

## 📌 Правило 01: Використовуйте офіційні образи / Rule 01: Use Official Images

- 🇺🇦 **Чому це важливо:** Офіційні образи на Docker Hub підтримуються профільними командами розробників, регулярно оновлюються, містять патчі безпеки та не містять шкідливого або застарілого коду.
- 🇬🇧 **Why it matters:** Official Docker Hub images are maintained by trusted teams, regularly patched for security vulnerabilities, and follow industry best practices.

```dockerfile
# ❌ Погано / Bad: Невідомий сторонній користувач (ризик вразливостей або бекдорів)
FROM randomuser123/python-flask:latest

# ✅ Добре / Good: Офіційний верифікований образ
FROM python:3.11-slim
```

---

## 📌 Правило 02: Ніколи не використовуйте tag `:latest` у продакшні / Rule 02: Don't ever use tag `:latest` in production

- 🇺🇦 **Чому це важливо:** Тег `:latest` не є фіксованою версією. Він може оновитися в будь-який момент. Через це ваш білд, який працював учора, сьогодні може зламатися через несумісні зміни у новій версії бібліотеки/мови.
- 🇬🇧 **Why it matters:** The `:latest` tag is mutable and points to the newest release, which can introduce breaking changes unexpectedly. It prevents reproducible builds and makes rollbacks hard.

```dockerfile
# ❌ Погано / Bad: Непередбачувано, версія може раптово змінитись
FROM node:latest
FROM postgres:latest

# ✅ Добре / Good: Точна, детермінована версія (Pinned version)
FROM node:20.11.0-alpine
FROM postgres:15.6-alpine
```

---

## 📌 Правило 03: Використовуйте найменші базові образи / Rule 03: Use smallest possible base image

- 🇺🇦 **Чому це важливо:** Менший образ = швидша передача через мережу (`docker pull`/`docker push`), швидший запуск контейнерів, менше споживання диску та значно менша поверхня атаки (менше встановлених утиліт = менше потенційних вразливостей CVE).
- 🇬🇧 **Why it matters:** Smaller base images reduce build times, network transfer times, disk usage, and minimize security vulnerabilities (smaller attack surface).

| Образ / Image | Приблизний розмір / Size | Призначення / Purpose |
| :--- | :--- | :--- |
| `python:3.11` (Full) | ~1000 MB | Містить повний набір компіляторів та системних утиліт |
| `python:3.11-slim` | ~120 MB | Містить тільки мінімальний Debian + Python runtime |
| `python:3.11-alpine` | ~50 MB | Ультралегкий дистрибутив Alpine на базі musl libc |

```dockerfile
# ❌ Погано / Bad: Зайві 900+ MB непотрібних пакетів
FROM python:3.11

# ✅ Добре / Good: Легкий та швидкий образ
FROM python:3.11-slim
```

---

## 📌 Правило 04: Не встановлюйте зайвих пакетів / Rule 04: Don't install unnecessary packages

- 🇺🇦 **Чому це важливо:** Не встановлюйте текстові редактори (`vim`, `nano`), засоби налагодження чи зайві бібліотеки у фінальний образ. Використовуйте прапорець `--no-install-recommends` для `apt-get` та очищуйте кеш пакетів.
- 🇬🇧 **Why it matters:** Avoid installing editors, build tools, or debug packages into final production images. Always use `--no-install-recommends` and clear package caches.

```dockerfile
# ❌ Погано / Bad: Встановлює сотні непотрібних рекомендованих пакетів і зберігає кеш на диску
RUN apt-get update && apt-get install -y curl vim git wget

# ✅ Добре / Good: Лише потрібні пакети, без зайвого + очищення кешу
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
```

---

## 📌 Правило 05: Використовуйте багатоетапні збірки / Rule 05: Use multi-stage builds

- 🇺🇦 **Чому це важливо:** Дозволяє відокремити важке середовище збірки (компілятори C/C++, SDK, dev-залежності) від фінального образу, де залишаються тільки скомпільовані бінарники або готові бібліотеки.
- 🇬🇧 **Why it matters:** Multi-stage builds keep compilation tools, intermediate files, and dev-dependencies out of the production runtime image.

```dockerfile
# --- Stage 1: Збірка / Build Stage ---
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# --- Stage 2: Чистий продакшн-образ / Production Stage ---
FROM python:3.11-slim
WORKDIR /app
# Копіюємо лише результат з етапу builder / Copy only artifacts from builder
COPY --from=builder /root/.local /root/.local
COPY . /app
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8080
CMD ["python", "app.py"]
```

---

## 📌 Правило 06: Один контейнер = один застосунок / Rule 06: Each container should run only one application

- 🇺🇦 **Чому це важливо:** Контейнер повинен вирішувати одне завдання (Single Responsibility Principle). Не запускайте веб-сервер, базу даних і Redis в одному контейнері. Це полегшує масштабування, перезапуск, збір логів та обробку сигналів зупинки (PID 1).
- 🇬🇧 **Why it matters:** Running one process per container ensures decoupled lifecycles, clear logging, independent horizontal scaling, and proper POSIX signal handling.

```
❌ Погано / Bad:
┌──────────────────────────────────────┐
│  Container: Web App + Postgres + SSH │
└──────────────────────────────────────┘

✅ Добре / Good (Docker Compose / Network):
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│  Container 1   │ <-> │  Container 2   │ <-> │  Container 3   │
│   (Web App)    │     │  (PostgreSQL)  │     │    (Redis)     │
└────────────────┘     └────────────────┘     └────────────────┘
```

---

## 📌 Правило 07: Кешування шарів (від стабільних до динамічних) / Rule 07: Use Layer Caching properly

- 🇺🇦 **Чому це важливо:** Docker кешує кожен шар згори донизу. Якщо шар змінюється, **всі наступні шари** перезбираються без кешу. Тому файли, які змінюються рідко (залежності), копіюють спочатку, а код, який змінюється постійно — в кінці.
- 🇬🇧 **Why it matters:** Docker caches layers sequentially. Order directives from least frequently changed (dependencies) to most frequently changed (source code) to speed up builds.

```dockerfile
# ❌ Погано / Bad: Будь-яка зміна в app.py змушує наново скачувати всі pip пакети!
COPY . /app
RUN pip install -r requirements.txt

# ✅ Добре / Good: Залежності кешуються і не встановлюються повторно при зміні коду
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
```

---

## 📌 Правило 08: Розбивайте довгі RUN команди на кілька рядків / Rule 08: Split long RUN commands

- 🇺🇦 **Чому це важливо:** Кожна інструкція `RUN` створює новий шар. Якщо розбити команди на кілька окремих `RUN`, тимчасові файли залишаться в проміжних шарах назавжди. Об'єднуйте їх через `&& \` для створення одного компактного шару та кращої читабельності.
- 🇬🇧 **Why it matters:** Group related commands into a single `RUN` using `&& \` to avoid creating unnecessary intermediate layers and make the Dockerfile readable.

```dockerfile
# ❌ Погано / Bad: Створює 4 окремих шари, тимчасовий кеш займає місце
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git
RUN rm -rf /var/lib/apt/lists/*

# ✅ Добре / Good: Один шар, легко читати, кеш очищено в тому ж шарі
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
```

---

## 📌 Правило 09: Віддавайте перевагу COPY над ADD / Rule 09: Prefer COPY over ADD

- 🇺🇦 **Чому це важливо:** `COPY` прозора, безпечна та просто копіює локальні файли. `ADD` має магічну приховану логіку (може автоматично розпаковувати архіви або завантажувати файли з URL), що часто призводить до неочікуваних багів. Використовуйте `ADD` виключно коли треба розпакувати локальний `.tar` архів.
- 🇬🇧 **Why it matters:** `COPY` is explicit, safe, and transparent. `ADD` has implicit behavior (auto-tar extraction and URL fetching). Only use `ADD` when you specifically need local tar auto-extraction.

```dockerfile
# ❌ Погано / Bad: Неочевидна поведінка для простих файлів
ADD requirements.txt /app/
ADD app.py /app/

# ✅ Добре / Good: Явно, просто і передбачувано
COPY requirements.txt /app/
COPY app.py /app/

# 💡 Виняток для ADD: Автоматичне розпакування архіву
ADD release-v1.0.tar.gz /app/
```

---

## 📌 Правило 10: ЗАВЖДИ використовуйте WORKDIR / Rule 10: ALWAYS use WORKDIR

- 🇺🇦 **Чому це важливо:** Ніколи не покладайтеся на початкову папку базового образу (вона може бути `/`, `/root` або будь-якою іншою). Також ніколи не пишіть `RUN cd /app`, оскільки команда `cd` **не зберігає свій стан між шарами Dockerfile**! `WORKDIR` автоматично створить папку, якщо її немає, і встановить контекст для всіх наступних інструкцій.
- 🇬🇧 **Why it matters:** Never rely on default base image working directories. Never use `RUN cd /app` (it doesn't persist across layers!). `WORKDIR` safely creates and sets the path for all subsequent instructions.

```dockerfile
# ❌ Погано / Bad: 'cd' діє ТІЛЬКИ в межах одного RUN і скидається на наступному рядку!
RUN mkdir /app
RUN cd /app
COPY app.py . # Файл потрапить у корінь або дефолтну папку, а не в /app!

# ✅ Добре / Good: Створює папку і надійно фіксує контекст
WORKDIR /app
COPY app.py .
```

---

## ⭐ Додаткові важливі правила / Bonus Critical Rules

### 🔒 11. Безпека: Не запускайте від `root` (Use Non-Root USER)
За замовчуванням контейнери виконуються з правами `root`. Якщо зловмисник зламає застосунок, він може отримати доступ до хост-системи.
```dockerfile
# Створення та перемикання на непривілейованого користувача
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser
```

### 🙈 12. Завжди створюйте `.dockerignore` (Always use .dockerignore)
Запобігає копіюванню секретів, локальних віртуальних середовищ (`.venv`, `node_modules`), історії `.git` та тимчасових файлів у контейнер.

### 🔑 13. Ніколи не зашивайте паролі та секрети у Dockerfile (Never Hardcode Secrets)
Використовуйте змінні середовища під час запуску (`docker run -e ...` / `--env-file`) або Docker Secrets.

### ⚡ 14. Використовуйте Exec Form для CMD та ENTRYPOINT (Use JSON Exec Form)
```dockerfile
# ❌ Shell Form: запускається через /bin/sh -c (сигнали SIGTERM блокуються, контейнер довго вимикається)
CMD python app.py

# ✅ Exec Form: запускається напряму (контейнер миттєво і коректно зупиняється)
CMD ["python", "app.py"]
```
