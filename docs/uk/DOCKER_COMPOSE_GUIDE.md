# 🐙 Повний Посібник по Docker Compose: Архітектура, Специфікація та Керування Мультиконтейнерними Стеками

Цей посібник містить вичерпну інформацію про роботу з **Docker Compose**, розбір специфікації файлу `docker-compose.yml`, повний довідник команд CLI, практичний аналіз стеку проекту (Flask + MySQL), тонкощі мереж, томів, змінних середовища та розв'язання типових проблем.

---

## 📑 Зміст

1. [Що таке Docker Compose та навіщо він потрібен](#1-що-таке-docker-compose-та-навіщо-він-потрібен)
2. [Еволюція Compose: V1 проти V2 та статус поля `version`](#2-еволюція-compose-v1-проти-v2-та-статус-поля-version)
3. [Анатомія та синтаксис файлу `docker-compose.yml`](#3-анатомія-та-синтаксис-файлу-docker-composeyml)
   - [Ключ `services` (Сервіси)](#ключ-services-сервіси)
   - [Ключ `networks` (Мережі)](#ключ-networks-мережі)
   - [Ключ `volumes` (Томи даних)](#ключ-volumes-томи-даних)
   - [Змінні середовища та файл `.env`](#змінні-середовища-та-файл-env)
4. [Практичний аналіз: Стек нашого проєкту (Flask + MySQL)](#4-практичний-аналіз-стек-нашого-проєкту-flask--mysql)
   - [Архітектурна схема](#архітектурна-схема)
   - [Порядковий розбір поточної конфігурації](#порядковий-розбір-поточної-конфігурації)
   - [Оптимізована версія з Healthcheck та .env](#оптимізована-версія-з-healthcheck-та-env)
5. [Повний довідник команд Docker Compose CLI](#5-повний-довідник-команд-docker-compose-cli)
   - [Запуск та збірка](#запуск-та-збірка)
   - [Моніторинг та перегляд стану](#моніторинг-та-перегляд-стану)
   - [Керування контейнерами (Stop / Start / Restart)](#керування-контейнерами-stop--start--restart)
   - [Виконання команд всередині сервісів](#виконання-команд-всередині-сервісів)
   - [Зупинка, очищення та видалення](#зупинка-очищення-та-видалення)
   - [Валідація та утиліти](#валідація-та-утиліти)
6. [Просунуті патерни та найкращі практики](#6-просунуті-патерни-та-найкращі-практики)
   - [Синхронізація запуску через Healthcheck](#синхронізація-запуску-через-healthcheck)
   - [Розділення оточень (Dev / Staging / Prod) через Overrides](#розділення-оточень-dev--staging--prod-через-overrides)
   - [Обмеження ресурсів (CPU та RAM)](#обмеження-ресурсів-cpu-та-ram)
   - [Безпека та секрети](#безпека-та-секрети)
7. [Типові помилки та Troubleshooting](#7-типові-помилки-та-troubleshooting)
8. [Шпаргалка швидкого пошуку команд](#8-шпаргалка-швидкого-пошуку-команд)

---

## 1. Що таке Docker Compose та навіщо він потрібен

У реальних проєктах застосунок рідко складається з одного контейнера. Зазвичай це екосистема: вебсервер, бекенд-додаток, реляційна база даних, кеш Redis, черги повідомлень (RabbitMQ/Kafka) тощо.

### Проблема ручного керування (`docker run`):
- Необхідно вручну створювати мережі (`docker network create`).
- Потрібно вручну створювати томи (`docker volume create`).
- Доводиться пам'ятати та вводити довгі команди з десятками аргументів (`-p`, `-v`, `-e`, `--network`, `--restart`, `--name`).
- Необхідно суворо дотримуватися черговості запуску (спочатку БД, потім бекенд).
- Складно синхронізувати конфігурацію між членами команди та CI/CD пайплайнами.

### Рішення: Docker Compose
**Docker Compose** — це інструмент декларативного опису та запуску мультиконтейнерних Docker-додатків. Вся архітектура інфраструктури проєкту фіксується в одному єдиному файлі — `docker-compose.yml`.

| Критерій | Звичайний Docker CLI (`docker run`) | Docker Compose (`docker compose`) |
| :--- | :--- | :--- |
| **Підхід** | Імперативний (покрокові команди) | Декларативний (опис бажаного кінцевого стану) |
| **Запуск усього стеку** | 5-10 окремих довгих команд | Одна команда: `docker compose up -d` |
| **Зупинка та очищення** | Зупинка й видалення кожного контейнера вручну | Одна команда: `docker compose down` |
| **Спільні мережі** | Створення мережі та підключення до неї кожного контейнера | Автоматичне створення ізольованої мережі проєкту за замовчуванням |
| **Повторюваність** | Залежить від людського фактора та bash-скриптів | 100% однакова поведінка на будь-якій машині |

---

## 2. Еволюція Compose: V1 проти V2 та статус поля `version`

> [!IMPORTANT]
> **Чому з'являється попередження:**
> `WARN[0000] docker-compose.yml: the attribute 'version' is obsolete, it will be ignored, please remove it to avoid potential confusion`

### Історичний контекст:
1. **Compose V1 (`docker-compose`)**: Був написаний на Python як окрема незалежна утиліта. Вимагав обов'язкового зазначення поля `version: '2'`, `version: '3'`, `version: '3.8'` на початку файлу, оскільки синтаксис змінювався від версії до версії.
2. **Compose V2 (`docker compose`)**: Повністю переписаний мовою Go та інтегрований безпосередньо в офіційний Docker CLI як плагін (через пробіл: `docker compose`, а не дефіс).
3. **Compose Specification (Сучасний стандарт)**: Формат об'єднано у відкриту [Compose Specification](https://compose-spec.io/). Тепер утиліта є динамічною та зворотно сумісною. Поле `version:` визнано **застарілим (obsolete)** і більше не потрібне.

### ❌ Застарілий підхід (Compose V1 / Старі версії):
```yaml
version: '3.8'  # ⚠️ Більше не потрібно! Викликає попередження у V2

services:
  web:
    image: nginx
```

### ✅ Сучасний стандарт (Compose Specification):
```yaml
# Поле version відсутнє — файл одразу починається з блоку services
services:
  web:
    image: nginx
```

---

## 3. Анатомія та синтаксис файлу `docker-compose.yml`

Файл `docker-compose.yml` використовує формат YAML. Основні кореневі секції:
- `services:` — опис контейнерів, їхніх образів, портів, змінних та залежностей.
- `networks:` — користувацькі мережі для ізоляції та комунікації сервісів.
- `volumes:` — іменовані томи для збереження постійних даних (персистентності).
- `configs:` / `secrets:` — керування конфігураціями та конфіденційними даними.

---

### Ключ `services` (Сервіси)

Кожен елемент під `services` визначає окремий контейнер.

```yaml
services:
  pythonapp:
    # 1. Збірка образу з локального Dockerfile
    build:
      context: .                           # Шлях до контексту збірки
      dockerfile: Dockerfile.multistage    # Назва файлу Dockerfile
      args:                                # Аргументи збірки (ARG)
        PYTHON_VERSION: "3.12.14"

    # 2. Назва образу та контейнера
    image: my-app:1.0                      # Тег для зібраного або завантаженого образу
    container_name: db-pythonapp           # Фіксоване ім'я контейнера замість автозгенерованого

    # 3. Прокидання портів (Host:Container)
    ports:
      - "8080:8080"                        # Доступний ззовні за адресою localhost:8080
      - "127.0.0.1:9000:9000"              # Прив'язка тільки до локального інтерфейсу хоста

    # 4. Внутрішні порти (тільки для інших контейнерів у спільній мережі)
    expose:
      - "5000"

    # 5. Змінні середовища
    environment:
      MY_ENV_VAR: development
      DATABASE_HOST: mysql                 # Ім'я іншого сервісу як DNS хост
      DATABASE_PORT: 3306
    env_file:                              # Або завантаження з файлу
      - .env

    # 6. Томи даних (Volumes & Bind Mounts)
    volumes:
      - db-data:/var/lib/mysql             # Іменований том (Named Volume)
      - ./logs:/app/logs                   # Монтування локальної папки (Bind Mount)
      - ./config.json:/app/config.json:ro  # Read-Only монтування одного файлу

    # 7. Мережі
    networks:
      - db-data-net

    # 8. Залежності та порядок старту
    depends_on:
      mysql:
        condition: service_healthy         # Чекати реальної готовності бази даних

    # 9. Політика перезапуску
    restart: unless-stopped                # no | always | on-failure | unless-stopped

    # 10. Перевизначення команди за замовчуванням
    command: ["python", "app.py", "--port", "8080"]
```

#### Політики перезапуску (`restart`):
- `no` (за замовчуванням): Контейнер не перезапускається автоматично.
- `always`: Контейнер завжди перезапускається у разі падіння або перезавантаження Docker-демона.
- `on-failure`: Перезапуск відбувається лише тоді, коли процес завершився з ненульовим кодом помилки.
- `unless-stopped`: Контейнер перезапускається завжди, крім випадків, коли його було зупинено вручну (`docker stop` / `docker compose stop`).

---

### Ключ `networks` (Мережі)

Docker Compose автоматично створює мережу за замовчуванням (`<назва_папки>_default`), де всі сервіси можуть спілкуватися за іменами сервісів завдяки вбудованому DNS-серверу Docker.

Ви також можете створювати власні ізольовані мережі:

```yaml
networks:
  # Користувацька bridge-мережа
  db-data-net:
    driver: bridge

  # Використання вже існуючої зовнішньої мережі
  pre-existing-network:
    external: true
    name: production-network
```

---

### Ключ `volumes` (Томи даних)

Іменовані томи керуються самим Docker і зберігаються у `/var/lib/docker/volumes/`. Вони не видаляються при зупинці чи оновленні контейнерів, що гарантує збереження даних бази даних.

```yaml
volumes:
  # Стандартний локальний том
  db-data:
    driver: local

  # Підключення існуючого зовнішнього тому
  external-volume:
    external: true
    name: shared_db_storage
```

---

### Змінні середовища та файл `.env`

Compose автоматично шукає файл `.env` у корені проєкту поруч із `docker-compose.yml` та підставляє значення у шаблон:

```bash
# Файл .env
APP_PORT=8080
DB_ROOT_PASS=secret1234
DB_NAME=app_db
DB_USER=app_user
DB_PASS=secret1234
```

```yaml
# Використання у docker-compose.yml
services:
  pythonapp:
    ports:
      - "${APP_PORT:-8080}:8080"           # Значення за замовчуванням :8080
    environment:
      - MYSQL_PASSWORD=${DB_PASS:?Помилка: DB_PASS обов'язковий!}
```

---

## 4. Практичний аналіз: Стек нашого проєкту (Flask + MySQL)

### Архітектурна схема

```
                      +-----------------------------------------------+
                      |          Docker Network: db-data-net          |
                      |                                               |
  Browser --------->  |   [ db-pythonapp ] (Flask App)                |
  (localhost:8080)    |   - Image: app:1.0                            |
                      |   - Port: 8080 -> 8080                        |
                      |   - Context: Dockerfile.multistage            |
                      |           |                                   |
                      |           | DNS resolution ("mysql:3306")     |
                      |           v                                   |
                      |   [ db-mysql ] (MySQL 8.x Server)             |
                      |   - Image: mysql:1.0                          |
                      |   - Port: 3306 -> 3306                        |
                      |   - Context: Dockerfile.mysql (init.sql)      |
                      |           |                                   |
                      +-----------|-----------------------------------+
                                  v
                       [ Named Volume: db-data ]
                       (/var/lib/mysql persistence)
```

---

### Порядковий розбір поточної конфігурації

Наш файл `docker-compose.yml` об'єднує два сервіси:

```yaml
networks:
  db-data-net:
    driver: bridge

services:
  pythonapp:
    image: app:1.0
    build:
      context: .
      dockerfile: Dockerfile.multistage
    container_name: db-pythonapp
    ports:
      - "8080:8080"
    environment:
      - MY_ENV_VAR=development
    networks:
      - db-data-net
    depends_on:
      - mysql
    restart: unless-stopped

  mysql:
    image: mysql:1.0
    build:
      context: .
      dockerfile: Dockerfile.mysql
    container_name: db-mysql
    ports:
      - "3306:3306"
    volumes:
      - db-data:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=1234
      - MYSQL_DATABASE=app_db
      - MYSQL_USER=app_user
      - MYSQL_PASSWORD=1234
    networks:
      - db-data-net
    
volumes:
  db-data:
    driver: local
```

#### Що тут відбувається:
1. **Мережа `db-data-net`**: Об'єднує сервіси `pythonapp` та `mysql`. Завдяки вбудованому DNS у Flask додатку (`app.py`) рядок підключення використовує хост `mysql`:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://app_user:1234@mysql:3306/app_db'
   ```
2. **Том `db-data`**: Прив'язаний до шляху `/var/lib/mysql` у контейнері MySQL. Якщо контейнер буде знищено та перестворено, всі записи таблиці `counter` збережуться.
3. **`depends_on: - mysql`**: Вказує Docker Compose запускати контейнер `db-mysql` перед `db-pythonapp`.

---

### Оптимізована версія з Healthcheck та .env

Базовий `depends_on` гарантує лише те, що контейнер MySQL *стартував*, але процес ініціалізації бази всередині може займати 5-15 секунд. Якщо Flask спробує підключитися негайно, виникне помилка `ConnectionRefusedError`.

Ось покращений патерн із перевіркою стану здоров'я (`healthcheck`):

```yaml
services:
  mysql:
    build:
      context: .
      dockerfile: Dockerfile.mysql
    container_name: db-mysql
    restart: unless-stopped
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-1234}
      MYSQL_DATABASE: ${MYSQL_DATABASE:-app_db}
      MYSQL_USER: ${MYSQL_USER:-app_user}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD:-1234}
    volumes:
      - db-data:/var/lib/mysql
    networks:
      - db-data-net
    # ✅ Healthcheck перевіряє реальну готовність приймати SQL-запити
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p1234"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s

  pythonapp:
    build:
      context: .
      dockerfile: Dockerfile.multistage
    container_name: db-pythonapp
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      MY_ENV_VAR: ${MY_ENV_VAR:-development}
    networks:
      - db-data-net
    # ✅ Чекаємо не просто старту, а проходження healthcheck у MySQL
    depends_on:
      mysql:
        condition: service_healthy

networks:
  db-data-net:
    driver: bridge

volumes:
  db-data:
    driver: local
```

---

## 5. Повний довідник команд Docker Compose CLI

> [!TIP]
> Усі команди наведено у сучасному стандарті Compose V2 (`docker compose ...`). Якщо у вашій системі встановлено стару утиліту V1, використовуйте `docker-compose ...`.

### Запуск та збірка

```bash
# Запуск усіх сервісів у фоновому режимі (detached mode)
docker compose up -d

# Запуск з примусовою перезбіркою образів (при зміні Dockerfile/коду)
docker compose up -d --build

# Запуск тільки одного конкретного сервісу та його залежностей
docker compose up -d pythonapp

# Примусове перестворення контейнерів, навіть якщо конфігурація не змінювалася
docker compose up -d --force-recreate

# Тільки збірка образів без запуску контейнерів
docker compose build

# Збірка без використання кешу
docker compose build --no-cache
```

---

### Моніторинг та перегляд стану

```bash
# Список працюючих контейнерів стеку
docker compose ps

# Список усіх контейнерів стеку (включаючи зупинені)
docker compose ps -a

# Перегляд потокових логів усіх сервісів у реальному часі
docker compose logs -f

# Логи тільки конкретного сервісу (наприклад, Flask додатку)
docker compose logs -f pythonapp

# Перегляд останніх 50 рядків логів із таймстемпами
docker compose logs -f --tail=50 -t mysql

# Перегляд запущених процесів у контейнерах
docker compose top
```

---

### Керування контейнерами (Stop / Start / Restart)

```bash
# Зупинка всіх працюючих сервісів (дані та контейнери зберігаються)
docker compose stop

# Запуск раніше зупинених сервісів
docker compose start

# Перезапуск усіх сервісів стеку
docker compose restart

# Перезапуск лише одного сервісу (наприклад, після зміни коду)
docker compose restart pythonapp

# Призупинення виконання процесів (SIGSTOP / pause)
docker compose pause

# Відновлення виконання процесів (unpause)
docker compose unpause
```

---

### Виконання команд всередині сервісів

```bash
# Виконати команду в уже запущеному контейнері (аналог docker exec)
docker compose exec pythonapp bash
docker compose exec mysql mysql -u app_user -p1234 app_db -e "SELECT * FROM counter;"

# Запустити одноразовий новий контейнер сервісу для виконання задачі та видалити його після завершення
docker compose run --rm pythonapp python -c "import app; print('App imported successfully')"
```

---

### Зупинка, очищення та видалення

```bash
# Зупинити та видалити контейнери й мережі проєкту
docker compose down

# ⚠️ Зупинити, видалити контейнери, мережі ТА іменовані томи (повне скидання БД!)
docker compose down -v

# Зупинити та видалити також образи, створені під час build
docker compose down --rmi all

# Видалити застарілі контейнери (orphans), які більше не описані в compose-файлі
docker compose down --remove-orphans
```

---

### Валідація та утиліти

```bash
# Перевірити синтаксис та відобразити фінальну обчислену конфігурацію (з підставленими змінними)
docker compose config

# Перевірити файл без зайвого виводу (тихий режим, повертає статус код)
docker compose config -q
```

---

## 6. Просунуті патерни та найкращі практики

### Синхронізація запуску через Healthcheck
Використання `condition: service_healthy` у `depends_on` усуває стан гонитви (race condition) між сервісами бази даних та додатками.

### Розділення оточень (Dev / Staging / Prod) через Overrides
Docker Compose автоматично об'єднує два файли: базовий `docker-compose.yml` та оверрайд `docker-compose.override.yml` (якщо він є поруч).

Для продакшну можна створити окремі файли конфігурації:
```bash
# Запуск розробницького оточення (дефолтний override підхоплюється автоматично)
docker compose up -d

# Запуск продакшн-конфігурації
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Приклад `docker-compose.override.yml` (для розробки — монтування вихідного коду на льоту):
```yaml
services:
  pythonapp:
    volumes:
      - .:/app                # Live-reload: зміни коду на хості миттєво видно в контейнері
    environment:
      - FLASK_DEBUG=1
```

---

### Обмеження ресурсів (CPU та RAM)
Щоб один неефективний сервіс не спожив усі ресурси хоста, встановлюйте ліміти:

```yaml
services:
  pythonapp:
    deploy:
      resources:
        limits:
          cpus: '0.50'        # Максимум 50% одного ядра CPU
          memory: 512M        # Максимум 512 МБ оперативної пам'яті
        reservations:
          cpus: '0.10'
          memory: 128M
```

---

### Безпека та секрети
- **Ніколи не комітьте паролі в Git**: Використовуйте `.env` та додайте його до `.gitignore`.
- **Створіть `.env.example`**: Опишіть назви необхідних змінних із фейковими значеннями для команди.
- **Не відкривайте зайві порти назовні**: Якщо база даних потрібна лише бекенду всередині Docker-мережі, не прокидайте `ports: - "3306:3306"` на хост у продакшні, використовуйте `expose: - "3306"`.

---

## 7. Типові помилки та Troubleshooting

### 1. `WARN: the attribute 'version' is obsolete`
- **Причина**: У файлі `docker-compose.yml` вказано перший рядок `version: '3'`.
- **Вирішення**: Просто видаліть рядок `version: ...`. Сучасний Compose V2 більше не потребує цього поля.

### 2. `Bind for 0.0.0.0:8080 failed: port is already allocated`
- **Причина**: Порт 8080 або 3306 вже зайнятий іншим процесом або стороннім контейнером.
- **Вирішення**:
  - Знайти процес: `sudo lsof -i :8080` або `sudo netstat -tulpn | grep 8080`
  - Змінити зовнішній порт у `docker-compose.yml`, наприклад: `ports: - "8081:8080"`.

### 3. `mysql.connector.errors.DatabaseError: 2003: Can't connect to MySQL server`
- **Причина**: Вебдодаток намагався підключитися до бази даних раніше, ніж сервіс MySQL закінчив внутрішню ініціалізацію, або використовується неправильне ім'я хоста.
- **Вирішення**:
  - Переконайтеся, що хост у рядку підключення відповідає назві сервісу: `@mysql:3306` (або `db-mysql`).
  - Додайте `healthcheck` у сервіс `mysql` та `condition: service_healthy` у `depends_on`.

### 4. Зміни в `init.sql` не застосовуються після перезапуску
- **Причина**: Скрипти з `/docker-entrypoint-initdb.d/` виконуються **лише один раз**, коли том бази даних порожній. Якщо том `db-data` вже існує, MySQL пропускає ініціалізацію.
- **Вирішення**: Перестворити том з повним очищенням:
  ```bash
  docker compose down -v
  docker compose up -d --build
  ```

### 5. Попередження `Found orphan containers`
- **Причина**: Раніше в compose-файлі був описаний сервіс, який потім видалили або перейменували, але старий контейнер залишився у системі.
- **Вирішення**: Запустити команду з прапорцем очищення:
  ```bash
  docker compose up -d --remove-orphans
  ```

---

## 8. Шпаргалка швидкого пошуку команд

| Дія | Команда |
| :--- | :--- |
| **Запуск у фоні** | `docker compose up -d` |
| **Перезбірка образів і запуск** | `docker compose up -d --build` |
| **Перегляд стану сервісів** | `docker compose ps` |
| **Перегляд живих логів** | `docker compose logs -f` |
| **Логи конкретного сервісу** | `docker compose logs -f pythonapp` |
| **Зупинка сервісів (без видалення)** | `docker compose stop` |
| **Запуск зупинених сервісів** | `docker compose start` |
| **Перезапуск одного сервісу** | `docker compose restart pythonapp` |
| **Виконати команду в контейнері** | `docker compose exec pythonapp bash` |
| **Зупинити та видалити контейнери/мережі** | `docker compose down` |
| **Повне видалення разом із томами (БД)** | `docker compose down -v` |
| **Перевірка валідності конфігурації** | `docker compose config` |
