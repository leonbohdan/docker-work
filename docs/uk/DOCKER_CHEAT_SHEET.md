# 🐳 Повний довідник та шпаргалка по Docker (Cheat Sheet)

Цей документ містить повний збірник інструкцій Dockerfile, команд керування образами, життєвого циклу контейнерів, роботи з мережами, томами (volumes), моніторингу та Docker Compose.

---

## 📑 Зміст
1. [Dockerfile: Інструкції та Архітектура](#1-dockerfile-інструкції-та-архітектура)
2. [Збірка та Управління Образами](#2-збірка-та-управління-образами)
3. [Створення та Життєвий Цикл Контейнерів](#3-створення-та-життєвий-цикл-контейнерів)
4. [Діагностика, Моніторинг та Exec](#4-діагностика-моніторинг-та-exec)
5. [Робота з Даними: Volumes та Bind Mounts](#5-робота-з-даними-volumes-та-bind-mounts)
6. [Мережі у Docker](#6-мережі-у-docker)
7. [Очищення Системи](#7-очищення-системи)
8. [Основи Docker Compose](#8-основи-docker-compose)
9. [Найкращі Практики та Поради](#9-найкращі-практики-та-поради)

---

## 1. Dockerfile: Інструкції та Архітектура

`Dockerfile` — це інструкція для автоматичної побудови образу (image). Кожен рядок створює новий шар (layer) у файловій системі образу.

### 📋 Таблиця Директив

| Директива | Опис | Приклад |
| :--- | :--- | :--- |
| `FROM` | Базовий образ (завжди перший рядок) | `FROM python:3.11-slim` |
| `WORKDIR` | Встановлює робочу директорію всередині контейнера | `WORKDIR /app` |
| `COPY` | Копіює локальні файли у контейнер | `COPY requirements.txt .` |
| `ADD` | Копіює файли; вміє розпаковувати `.tar` та завантажувати URL | `ADD app.tar.gz /app/` |
| `RUN` | Виконує команди під час збірки образу (створює шар) | `RUN pip install -r requirements.txt` |
| `ENV` | Встановлює постійні змінні середовища | `ENV PORT=8080 ENV=production` |
| `ARG` | Змінні, доступні **тільки** під час збірки образу | `ARG APP_VERSION=1.0.0` |
| `EXPOSE` | Документує порти, які слухає контейнер (не відкриває їх на хості автоматично!) | `EXPOSE 8080` |
| `USER` | Встановлює користувача (безпека: уникайте `root`) | `USER appuser` |
| `VOLUME` | Створює точку монтування для збереження даних | `VOLUME ["/app/data"]` |
| `ENTRYPOINT` | Головний виконуваний файл/команда контейнера | `ENTRYPOINT ["python", "app.py"]` |
| `CMD` | Аргументи за замовчуванням для `ENTRYPOINT` або дефолтна команда | `CMD ["--port", "8080"]` |
| `HEALTHCHECK`| Інструкція для перевірки працездатності сервісу | `HEALTHCHECK --interval=30s CMD curl -f http://localhost:8080/ \|\| exit 1` |

---

### 🔍 Детальні відмінності

#### 1. `CMD` vs `ENTRYPOINT`
- **`ENTRYPOINT`** визначає *що саме* запускається (фіксована бінарна команда).
- **`CMD`** надає *параметри за замовчуванням*, які користувач може легко замінити при виклику `docker run`.
- **Рекомендований формат (Exec Form)**: завжди використовуйте JSON-масив: `["executable", "param1", "param2"]`, щоб уникнути зайвого shell-процесу (`/bin/sh -c`) і коректно передавати системні сигнали (SIGTERM).

```dockerfile
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

## 2. Збірка та Управління Образами

### 🔨 Створення власного образу

```bash
# Зібрати образ з поточного каталогу (з тегом name:tag)
docker build -t my-app:1.0 .

# Збірка з конкретного Dockerfile (якщо назва відрізняється)
docker build -f Dockerfile.multistage -t my-app:multistage .

# Збірка без використання кешу (чиста перезбірка)
docker build --no-cache -t my-app:1.0 .

# Передача аргументів збірки (ARG)
docker build --build-arg APP_VERSION=2.0.0 -t my-app:2.0.0 .

# Збірка конкретного етапу у multi-stage build
docker build --target builder -t my-app:builder .
```

### 📦 Управління образами

```bash
# Переглянути всі збережені локальні образи
docker images
# або
docker image ls

# Додати новий тег існуючому образу
docker tag my-app:1.0 myusername/my-app:1.0

# Видалити образ
docker rmi my-app:1.0

# Примусово видалити образ
docker rmi -f my-app:1.0

# Видалити "завислі" неіменовані образи (dangling images: <none>)
docker image prune

# Видалити ВСІ невикористовувані образи
docker image prune -a

# Подивитися історію шарів образу
docker history my-app:1.0

# Експорт образу у .tar архів (для перенесення офлайн)
docker save -o my-app.tar my-app:1.0

# Імпорт образу з .tar архіву
docker load -i my-app.tar

# Завантажити образ на Docker Hub / Registry
docker push myusername/my-app:1.0

# Завантажити образ з реєстру
docker pull python:3.11-slim
```

---

## 3. Створення та Життєвий Цикл Контейнерів

### 🚀 Запуск контейнера (`docker run`)

```bash
# 1. Повний приклад запуску вебсервера:
docker run -d \
  --name web-app \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -e ENV=production \
  --restart unless-stopped \
  my-app:1.0

# 2. Інтерактивний запуск з терміналом (для налагодження)
docker run -it --rm --name debug-container python:3.11-slim /bin/bash
```

#### 🔑 Головні прапори `docker run`:

| Прапор | Опис |
| :--- | :--- |
| `-d` (`--detach`) | Фоновий режим (контейнер працює у бекграунді) |
| `-it` | Інтерактивний режим + псевдо-термінал |
| `--name <name>` | Власне ім'я для контейнера |
| `-p <host>:<cont>` | Прокидання порту: `<порт_хоста>:<порт_контейнера>` |
| `-v <host>:<cont>` | Монтування директорії (Bind mount або Volume) |
| `-e KEY=VAL` | Передача змінної середовища |
| `--env-file <file>` | Завантаження змінних з `.env` файлу |
| `--rm` | Автоматично видалити контейнер після його зупинки |
| `--restart <policy>`| Політика перезапуску (`no`, `always`, `unless-stopped`, `on-failure`) |
| `--network <net>` | Підключення до кастомної мережі |
| `-m 512m` | Обмеження оперативної пам'яті (RAM) |
| `--cpus="1.5"` | Обмеження кількості ядер процесора |

---

### 🕹️ Управління станом контейнерів

```bash
# Список тільки запущених контейнерів
docker ps

# Список УСІХ контейнерів (і запущених, і зупинених)
docker ps -a

# Зупинити працюючий контейнер (SIGTERM -> SIGKILL через 10с)
docker stop web-app

# Примусово вбити контейнер миттєво (SIGKILL)
docker kill web-app

# Запустити раніше зупинений контейнер
docker start web-app

# Перезапустити контейнер
docker restart web-app

# Призупинити всі процеси контейнера (freeze)
docker pause web-app

# Відновити процеси контейнера
docker unpause web-app

# Видалити зупинений контейнер
docker rm web-app

# Примусово зупинити і видалити контейнер
docker rm -f web-app

# Видалити ВСІ зупинені контейнери
docker container prune
```

---

## 4. Діагностика, Моніторинг та Exec

```bash
# Перегляд логів контейнера
docker logs web-app

# Перегляд логів у реальному часі (live stream) + останні 100 рядків
docker logs -f --tail 100 web-app

# Зайти всередину ПРАЦЮЮЧОГО контейнера в інтерактивному шеллі
docker exec -it web-app /bin/bash
# або (для Alpine / slim):
docker exec -it web-app /bin/sh

# Виконати окрему одноразову команду всередині контейнера
docker exec web-app ls -la /app

# Скопіювати файл з хоста у контейнер
docker cp ./config.json web-app:/app/config.json

# Скопіювати файл з контейнера на хост
docker cp web-app:/app/logs.txt ./logs.txt

# Детальна JSON-інформація про контейнер або образ
docker inspect web-app

# Отримати тільки IP-адресу контейнера через фільтр
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' web-app

# Моніторинг використання ресурсів у реальному часі (CPU, RAM, Net I/O)
docker stats

# Перегляд запущених процесів всередині контейнера
docker top web-app

# Перевірити зміни файлової системи контейнера
docker diff web-app
```

---

## 5. Робота з Даними: Volumes та Bind Mounts

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
docker volume create app_data

# Переглянути список volumes
docker volume ls

# Отримати детальну інформацію про volume
docker volume inspect app_data

# Використання при запуску контейнера
docker run -d --name db -v app_data:/var/lib/mysql mysql:8.0

# Видалити конкретний volume
docker volume rm app_data

# Видалити всі невикористовувані volumes
docker volume prune
```

### 📂 2. Bind Mounts (Монтування конкретної папки з комп'ютера — для розробки)

```bash
# Монтування поточної папки хоста у /app всередині контейнера
docker run -d -p 8080:8080 -v $(pwd):/app --name dev-server my-app:1.0
```

---

## 6. Мережі у Docker

За замовчуванням контейнери запускаються в мережі `bridge`. Для безпечного та зручного спілкування між контейнерами за їхніми **іменами** (DNS resolution) створюють власні мережі.

```bash
# Створити користувацьку bridge-мережу
docker network create my-network

# Переглянути список мереж
docker network ls

# Запустити контейнери в одній мережі
docker run -d --name database --network my-network mysql:8.0
docker run -d --name web --network my-network -p 8080:8080 my-app:1.0
# Тепер 'web' може звертатися до бази за хостом 'database'!

# Підключити вже запущений контейнер до мережі
docker network connect my-network other-container

# Відключити контейнер від мережі
docker network disconnect my-network other-container

# Інспекція мережі (хто підключений, IP-адреси)
docker network inspect my-network

# Видалити мережу
docker network rm my-network

# Видалити всі невикористовувані мережі
docker network prune
```

---

## 7. Очищення Системи

Коли закінчується вільне місце на диску:

```bash
# Перевірити, скільки місця займає Docker
docker system df

# Детальний звіт по використанню диску
docker system df -v

# Стандартне очищення: зупинені контейнери, невикористовувані мережі, завислі образи
docker system prune

# ПОВНЕ агресивне очищення: ВСІ зупинені контейнери, ВСІ невикористовувані образи і томи
docker system prune -a --volumes
```

---

## 8. Основи Docker Compose

Для запуску мультиконтейнерних додатків використовують `docker compose` з файлом `docker-compose.yml`.

### Приклад `docker-compose.yml`:
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
      - db
    restart: unless-stopped

  db:
    image: mysql:8.0
    container_name: mysql-db
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: app_db
    ports:
      - "3306:3306"
    volumes:
      - db_data:/var/lib/mysql
    restart: always

volumes:
  db_data:
```

### ⚡ Шпаргалка команд Docker Compose:

```bash
# Запустити всі сервіси у фоновому режимі (та зібрати образи, якщо треба)
docker compose up -d

# Примусово перезібрати образи перед запуском
docker compose up -d --build

# Переглянути статус сервісів
docker compose ps

# Живі логи всіх сервісів разом
docker compose logs -f

# Логи конкретного сервісу
docker compose logs -f web

# Зупинити та видалити контейнери й мережі
docker compose down

# Зупинити та видалити все, ВКЛЮЧАЮЧИ volumes
docker compose down -v

# Виконати команду в контексті сервісу
docker compose exec web /bin/sh
```

---

## 9. Найкращі Практики та Поради

1. **Кешування шарів (Layer Caching)**:
   - Розміщуйте інструкції, які змінюються рідко (наприклад, копіювання `requirements.txt` та інсталяція залежностей), **перед** копіюванням коду самого проєкту (`COPY . .`).
2. **Зменшення кількості шарів**:
   - Об'єднуйте пов'язані `RUN` команди через `&&` та очищуйте кеш пакетних менеджерів в одному шарі:
     ```dockerfile
     RUN apt-get update && apt-get install -y --no-install-recommends \
         curl \
         ca-certificates \
         && rm -rf /var/lib/apt/lists/*
     ```
3. **Безпека (Security)**:
   - Не запускайте додатки від імені `root`. Створюйте непривілейованого користувача через `USER`.
   - Не записуйте секрети, паролі чи API-ключі у `Dockerfile` або `ENV`. Використовуйте `.env` файли або Secret Management.
4. **Легкі базові образи**:
   - Віддавайте перевагу `alpine` або `slim` образам (наприклад, `python:3.11-slim` замість `python:3.11`).
5. **Фіксація версій (Pin versions)**:
   - Уникайте тегу `:latest` для продакшну. Завжди явно вказуйте версію: `python:3.12.14-slim`.
6. **Завжди створюйте `.dockerignore`**:
   - Це запобігає випадковому потраплянню секретів, `.venv`, `node_modules` та важких файлів у контекст збірки.
