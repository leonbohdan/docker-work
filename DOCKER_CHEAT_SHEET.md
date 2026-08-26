# 🐳 Docker Ultimate Reference Guide & Cheat Sheet
### 🇺🇦 Довідник та Шпаргалка по Docker | 🇬🇧 Comprehensive Docker Guide & Cheat Sheet

---

## 📑 Зміст / Table of Contents
1. [Dockerfile: Інструкції та Архітектура / Instructions & Architecture](#1-dockerfile-інструкції-та-архітектура--instructions--architecture)
2. [Збірка та Управління Образами / Image Building & Management](#2-збірка-та-управління-образами--image-building--management)
3. [Створення та Життєвий Цикл Контейнерів / Container Lifecycle & Execution](#3-створення-та-життєвий-цикл-контейнерів--container-lifecycle--execution)
4. [Діагностика, Моніторинг та Exec / Debugging, Monitoring & Exec](#4-діагностика-моніторинг-та-exec--debugging-monitoring--exec)
5. [Робота з Даними: Volumes та Bind Mounts / Data Persistence](#5-робота-з-даними-volumes-та-bind-mounts--data-persistence)
6. [Мережі у Docker / Docker Networking](#6-мережі-у-docker--docker-networking)
7. [Очищення Системи / System Cleanup & Maintenance](#7-очищення-системи--system-cleanup--maintenance)
8. [Основи Docker Compose / Docker Compose Basics](#8-основи-docker-compose--docker-compose-basics)
9. [Найкращі Практики та Поради / Best Practices & Tips](#9-найкращі-практики-та-поради--best-practices--tips)

---

## 1. Dockerfile: Інструкції та Архітектура / Instructions & Architecture

`Dockerfile` — це інструкція для автоматичної побудови образу (image). Кожен рядок створює новий шар (layer) у файловій системі образу.

### 📋 Таблиця Директив / Directives Reference

| Директива / Directive | Опис (UA) 🇺🇦 | Description (EN) 🇬🇧 | Приклад / Example |
| :--- | :--- | :--- | :--- |
| `FROM` | Базовий образ (завжди перший рядок) | Base image to build upon (must be 1st line) | `FROM python:3.11-slim` |
| `WORKDIR` | Встановлює робочу директорію всередині контейнера | Sets the working directory inside container | `WORKDIR /app` |
| `COPY` | Копіює локальні файли у контейнер | Copies files/dirs from host into container | `COPY requirements.txt .` |
| `ADD` | Копіює файли; вміє розпаковувати `.tar` та завантажувати URL | Copies files; auto-extracts `.tar` & supports URLs | `ADD app.tar.gz /app/` |
| `RUN` | Виконує команди під час збірки образу (створює шар) | Executes command during build time (creates layer) | `RUN pip install -r requirements.txt` |
| `ENV` | Встановлює постійні змінні середовища | Sets persistent environment variables | `ENV PORT=8080 ENV=production` |
| `ARG` | Змінні, доступні **тільки** під час збірки образу | Variables available **only** at build time | `ARG APP_VERSION=1.0.0` |
| `EXPOSE` | Документує порти, які слухає контейнер (не відкриває їх на хості автоматично!) | Informs Docker of runtime port listening (docs only) | `EXPOSE 8080` |
| `USER` | Встановлює користувача (безпека: уникайте `root`) | Sets non-root user UID/name for commands | `USER appuser` |
| `VOLUME` | Створює точку монтування для збереження даних | Creates a mount point for external data persistence | `VOLUME ["/app/data"]` |
| `ENTRYPOINT` | Головний виконуваний файл/команда контейнера | Default executable process that cannot be overridden easily | `ENTRYPOINT ["python", "app.py"]` |
| `CMD` | Аргументи за замовчуванням для `ENTRYPOINT` або дефолтна команда | Default arguments or command (easily overridden) | `CMD ["--port", "8080"]` |
| `HEALTHCHECK`| Інструкція для перевірки працездатності сервісу | Checks if the container service is healthy | `HEALTHCHECK --interval=30s CMD curl -f http://localhost:8080/ || exit 1` |

---

### 🔍 Детальні відмінності / Key Differences to Know

#### 1. `CMD` vs `ENTRYPOINT`
- **`ENTRYPOINT`** визначає *що саме* запускається (фіксована бінарна команда).
- **`CMD`** надає *параметри за замовчуванням*, які користувач може легко замінити при виклику `docker run`.
- **Рекомендований формат (Exec Form)**: завжди використовуйте JSON-масив: `["executable", "param1", "param2"]`, щоб уникнути зайвого shell-процесу (`/bin/sh -c`) і коректно передавати системні сигнали (SIGTERM).

```dockerfile
# ENTRYPOINT + CMD Патерн
ENTRYPOINT ["python", "app.py"]
CMD ["--host", "0.0.0.0", "--port", "8080"]
```
> Якщо запустити `docker run my-image --port 9000`, аргументи з `CMD` заміняться на `--port 9000`.

#### 2. `COPY` vs `ADD`
- **Завжди віддавайте перевагу `COPY`** для простого копіювання файлів.
- Використовуйте `ADD` лише тоді, коли потрібно автоматично розпакувати локальний архів (`.tar`, `.tar.gz`) безпосередньо у контейнер.

#### 3. Багатоетапні збірки (Multi-Stage Builds)
Дозволяють створювати легкі фінальні образи, відокремлюючи середовище компіляції/збірки від середовища виконання:

```dockerfile
# --- Stage 1: Build & Dependencies ---
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Stage 2: Final Production Image ---
FROM python:3.11-slim
WORKDIR /app
# Копіюємо лише встановлені пакети з першого етапу / Copy only installed packages
COPY --from=builder /root/.local /root/.local
COPY app.py .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8080
CMD ["python", "app.py"]
```

#### 4. `.dockerignore`
Файл у корені проєкту, який виключає зайві файли з контексту збірки (прискорює збірку і зменшує розмір):
```text
.git
.venv
__pycache__
*.pyc
node_modules
.env
Dockerfile*
README.md
```

---

## 2. Збірка та Управління Образами / Image Building & Management

### 🔨 Створення власного образу / Building Custom Images

```bash
# Зібрати образ з поточного каталогу (з тегом name:tag)
# Build image from current directory
docker build -t my-app:1.0 .

# Збірка з конкретного Dockerfile (якщо назва відрізняється)
# Build from specific Dockerfile
docker build -f Dockerfile.multistage -t my-app:multistage .

# Збірка без використання кешу (чиста перезбірка)
# Build without cache
docker build --no-cache -t my-app:1.0 .

# Передача аргументів збірки (ARG)
# Pass build arguments
docker build --build-arg APP_VERSION=2.0.0 -t my-app:2.0.0 .

# Збірка конкретного етапу у multi-stage build
# Build a specific multi-stage target
docker build --target builder -t my-app:builder .
```

### 📦 Управління образами / Managing Images

```bash
# Переглянути всі збережені локальні образи
# List local images
docker images
# або / or
docker image ls

# Додати новий тег існуючому образу
# Tag image (e.g., for Docker Hub or private registry)
docker tag my-app:1.0 myusername/my-app:1.0

# Видалити образ
# Remove an image
docker rmi my-app:1.0

# Примусово видалити образ (навіть якщо використовується зупиненим контейнером)
# Force remove image
docker rmi -f my-app:1.0

# Видалити "завислі" неіменовані образи (dangling images: <none>)
# Remove dangling images
docker image prune

# Видалити ВСІ невикористовувані образи
# Remove all unused images
docker image prune -a

# Подивитися історію шарів образу
# View history/layers of an image
docker history my-app:1.0

# Експорт образу у .tar архів (для перенесення офлайн)
# Save image to tarball
docker save -o my-app.tar my-app:1.0

# Імпорт образу з .tar архіву
# Load image from tarball
docker load -i my-app.tar

# Завантажити образ на Docker Hub / Registry
# Push image to registry
docker push myusername/my-app:1.0

# Завантажити образ з реєстру
# Pull image from registry
docker pull python:3.11-slim
```

---

## 3. Створення та Життєвий Цикл Контейнерів / Container Lifecycle & Execution

### 🚀 Запуск контейнера (`docker run`) / Running Containers

Команда `docker run` створює і відразу запускає новий контейнер з вказаного образу.

```bash
# Основний синтаксис / Basic syntax:
# docker run [FLAGS] IMAGE [COMMAND] [ARG...]

# 1. Повний бойовий приклад запуску веб-сервера:
# Full production-like web server launch:
docker run -d \
  --name web-app \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -e ENV=production \
  --restart unless-stopped \
  my-app:1.0

# 2. Інтерактивний запуск з терміналом (корисно для налагодження)
# Interactive terminal run (useful for debug)
docker run -it --rm --name debug-container python:3.11-slim /bin/bash
```

#### 🔑 Головні прапори `docker run` / Essential `docker run` Flags:

| Прапор / Flag | Опис (UA) 🇺🇦 | Description (EN) 🇬🇧 |
| :--- | :--- | :--- |
| `-d` (`--detach`) | Фоновий режим (контейнер працює у бекграунді) | Run container in background (detached mode) |
| `-it` | Інтерактивний режим + псевдо-термінал | Interactive mode + allocate pseudo-TTY (for bash/sh) |
| `--name <name>` | Власне ім'я для контейнера (замість випадкового) | Assign a friendly name to the container |
| `-p <host>:<cont>` | Прокидання порту: `<порт_хоста>:<порт_контейнера>` | Port publishing: `<host_port>:<container_port>` |
| `-v <host>:<cont>` | Монтування директорії (Bind mount або Volume) | Mount volume or host directory into container |
| `-e KEY=VAL` | Передача змінної середовища | Set an environment variable |
| `--env-file <file>` | Завантаження змінних з `.env` файлу | Read environment variables from a file |
| `--rm` | Автоматично видалити контейнер після його завершення | Automatically remove container when it exits |
| `--restart <policy>`| Політика перезапуску (`no`, `always`, `unless-stopped`, `on-failure`) | Container restart policy |
| `--network <net>` | Підключення до кастомної мережі | Connect container to a specific network |
| `-m 512m` | Обмеження оперативної пам'яті (RAM) | Memory limit |
| `--cpus="1.5"` | Обмеження кількості ядер процесора | CPU limit |

---

### 🕹️ Управління станом контейнерів / Managing Container State

```bash
# Список тільки запущених контейнерів
# List running containers
docker ps

# Список УСІХ контейнерів (і запущених, і зупинених)
# List all containers (running + stopped)
docker ps -a

# Зупинити працюючий контейнер (сигнал SIGTERM -> SIGKILL через 10с)
# Stop a running container gracefully
docker stop web-app

# Примусово вбити контейнер миттєво (SIGKILL)
# Kill a container immediately
docker kill web-app

# Запустити раніше зупинений контейнер
# Start a stopped container
docker start web-app

# Перезапустити контейнер
# Restart container
docker restart web-app

# Призупинити всі процеси контейнера (freeze)
# Pause all processes in container
docker pause web-app

# Відновити процеси контейнера
# Unpause container
docker unpause web-app

# Видалити зупинений контейнер
# Remove a stopped container
docker rm web-app

# Примусово зупинити і видалити контейнер за 1 команду
# Force stop and remove running container
docker rm -f web-app

# Видалити ВСІ зупинені контейнери
# Remove all stopped containers
docker container prune
```

---

## 4. Діагностика, Моніторинг та Exec / Debugging, Monitoring & Exec

```bash
# Перегляд логів контейнера
# View container logs
docker logs web-app

# Перегляд логів у реальному часі (live stream) + останні 100 рядків
# Follow logs live + show last 100 lines
docker logs -f --tail 100 web-app

# Зайти всередину ПРАЦЮЮЧОГО контейнера в інтерактивному шеллі
# Execute interactive shell inside RUNNING container
docker exec -it web-app /bin/bash
# або (якщо немає bash, для Alpine/slim):
# or (for Alpine/minimal images without bash):
docker exec -it web-app /bin/sh

# Виконати окрему одноразову команду всередині працюючого контейнера
# Run single command inside container without opening shell
docker exec web-app ls -la /app

# Скопіювати файл з хоста у контейнер
# Copy file from host into container
docker cp ./config.json web-app:/app/config.json

# Скопіювати файл з контейнера на хост
# Copy file from container to host
docker cp web-app:/app/logs.txt ./logs.txt

# Детальна технічна JSON-інформація про контейнер або образ (IP, порти, mounts, env)
# Detailed JSON inspection (IP, mounts, state, network)
docker inspect web-app

# Отримати тільки IP-адресу контейнера через фільтр
# Get container IP address directly
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' web-app

# Моніторинг використання ресурсів у реальному часі (CPU, RAM, Net I/O)
# Live resource usage metrics
docker stats

# Перегляд запущених процесів всередині контейнера
# View running processes inside container
docker top web-app

# Перевірити зміни файлової системи контейнера (порівняно з початковим образом)
# Inspect filesystem changes
docker diff web-app
```

---

## 5. Робота з Даними: Volumes та Bind Mounts / Data Persistence

У контейнерах файлова система за замовчуванням є тимчасовою (ephemeral) — після видалення контейнера всі дані зникають. Для постійного збереження використовують **Volumes** або **Bind Mounts**.

```
Хост (Host Machine)                       Контейнер (Container)
┌────────────────────────────────┐       ┌────────────────────────────┐
│ /var/lib/docker/volumes/my-vol │ ────> │ /app/data  (Named Volume)  │
│ /home/user/project/src         │ ────> │ /app/src   (Bind Mount)    │
└────────────────────────────────┘       └────────────────────────────┘
```

### 📁 1. Named Volumes (Керуються Докером — рекомендовано для БД та даних)

```bash
# Створити volume
# Create volume
docker volume create app_data

# Переглянути список volumes
# List volumes
docker volume ls

# Отримати детальну інформацію про volume
# Inspect volume
docker volume inspect app_data

# Використання при запуску контейнера
# Mount named volume in docker run
docker run -d --name db -v app_data:/var/lib/postgresql/data postgres:15

# Видалити конкретний volume
# Remove volume
docker volume rm app_data

# Видалити всі невикористовувані volumes
# Remove all dangling/unused volumes
docker volume prune
```

### 📂 2. Bind Mounts (Монтування конкретної папки з вашого комп'ютера — ідеально для розробки)

```bash
# Монтування поточної папки хоста у /app всередині контейнера
# Mount current directory into container (Hot-reload / development)
docker run -d -p 8080:8080 -v $(pwd):/app --name dev-server my-app:1.0
```

---

## 6. Мережі у Docker / Docker Networking

За замовчуванням контейнери запускаються в мережі `bridge`. Для безпечного та зручного спілкування між контейнерами за їхніми **іменами** (DNS resolution) створюють власні мережі.

```bash
# Створити користувацьку bridge-мережу
# Create a custom user-defined network
docker network create my-network

# Переглянути список мереж
# List all networks
docker network ls

# Запустити контейнери в одній мережі
# Run containers on the same network
docker run -d --name database --network my-network postgres:15
docker run -d --name web --network my-network -p 8080:8080 my-app:1.0
# Тепер 'web' може звертатися до бази просто за хостом 'database'!
# Now 'web' can reach PostgreSQL using hostname 'database'!

# Підключити вже запущений контейнер до мережі
# Connect running container to network
docker network connect my-network other-container

# Відключити контейнер від мережі
# Disconnect container from network
docker network disconnect my-network other-container

# Інспекція мережі (хто підключений, IP-адреси)
# Inspect network
docker network inspect my-network

# Видалити мережу
# Remove network
docker network rm my-network

# Видалити всі невикористовувані мережі
# Remove unused networks
docker network prune
```

---

## 7. Очищення Системи / System Cleanup & Maintenance

Коли закінчується вільне місце на диску через старі образи, логи та контейнери:

```bash
# Перевірити, скільки місця займає Docker
# Show Docker disk usage
docker system df

# Детальний звіт по використанню диску
# Verbose disk usage
docker system df -v

# 🧹 Стандартне очищення: видаляє зупинені контейнери, невикористовувані мережі, завислі образи
# Safe cleanup: stopped containers, dangling images, unused networks
docker system prune

# 💥 ПОВНЕ агресивне очищення: видаляє ВСІ зупинені контейнери, ВСІ невикористовувані образи і томи
# DEEP cleanup: removes all stopped containers, unused networks, volumes and all unused images
docker system prune -a --volumes
```

---

## 8. Основи Docker Compose / Docker Compose Basics

Для запуску мульти-контейнерних додатків (наприклад, Web + Database + Redis) використовують `docker compose` з файлом `compose.yaml` або `docker-compose.yml`.

### Приклад `compose.yaml`:
```yaml
version: '3.8'

services:
  web:
    build: .
    container_name: flask-web
    ports:
      - "8080:8080"
    environment:
      - ENV=development
    volumes:
      - .:/app
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: redis-cache
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: always

volumes:
  redis_data:
```

### ⚡ Шпаргалка команд Docker Compose / Compose Commands:

```bash
# Запустити всі сервіси у фоновому режимі (та зібрати образи, якщо треба)
# Start all services detached (and build if needed)
docker compose up -d

# Примусово перезібрати образи перед запуском
# Force rebuild images and start
docker compose up -d --build

# Переглянути статус сервісів
# Check running services
docker compose ps

# Живі логи всіх сервісів разом
# Live logs from all services
docker compose logs -f

# Логи конкретного сервісу
# Logs for a specific service
docker compose logs -f web

# Зупинити та видалити контейнери й мережі
# Stop and remove containers and networks
docker compose down

# Зупинити та видалити все, ВКЛЮЧАЮЧИ volumes (обережно з даними!)
# Stop and remove everything INCLUDING volumes
docker compose down -v

# Виконати команду в контексті сервісу
# Exec command in compose service
docker compose exec web /bin/sh
```

---

## 9. Найкращі Практики та Поради / Best Practices & Tips

1. **Кешування шарів (Layer Caching)**:
   - Розміщуйте інструкції, які змінюються рідко (наприклад, встановлення системних пакетів, копіювання `requirements.txt` / `package.json` та інсталяція залежностей), **перед** копіюванням коду самого проєкту (`COPY . .`).
2. **Зменшення кількості шарів**:
   - Об'єднуйте пов'язані `RUN` команди через `&&` та очищуйте кеш пакетних менеджерів в одному шарі:
     ```dockerfile
     RUN apt-get update && apt-get install -y --no-install-recommends \
         curl \
         ca-certificates \
         && rm -rf /var/lib/apt/lists/*
     ```
3. **Безпека (Security)**:
   - Не запускайте додатки від імені `root`. Створюйте користувача через `USER`.
   - Не записуйте секрети, паролі чи API-ключі у `Dockerfile` або `ENV`. Використовуйте `.env` файли або Secret Management.
4. **Використовуйте легкі базові образи**:
   - Віддавайте перевагу `alpine` або `slim` образам (наприклад, `python:3.11-slim` замість важкого `python:3.11`).
5. **Фіксація версій (Pin versions)**:
   - Уникайте тегу `:latest` для продакшну. Завжди явно вказуйте версію: `python:3.11.8-slim`.
6. **Завжди створюйте `.dockerignore`**:
   - Це запобігає випадковому потраплянню секретів, локальних віртуальних середовищ (`.venv`, `node_modules`) та важких файлів у контекст збірки.
