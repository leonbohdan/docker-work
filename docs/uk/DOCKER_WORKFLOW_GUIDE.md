# 🐳 Посібник по роботі з Docker: Flask + MySQL + Multi-Container Architecture

Цей документ фіксує структуру контейнеризації проекту, принципи взаємодії сервісів (Flask App + MySQL), багатоетапні збірки (Multi-stage builds), роботу з мережами, томами (volumes) та підключення клієнтів (CLI / MySQL Workbench).

---

## 📑 Зміст
1. [Архітектура проекту](#1-архітектура-проекту)
2. [Опис ключових файлів](#2-опис-ключових-файлів)
3. [Покрокова інструкція запуску](#3-покрокова-інструкція-запуску)
   - [Варіант А: Рекомендований (Користувацька мережа з DNS)](#варіант-а-рекомендований-користувацька-мережа-з-dns)
   - [Варіант Б: Запуск у дефолтній мережі bridge (за IP)](#варіант-б-запуск-у-дефолтній-мережі-bridge-за-ip)
4. [Підключення до бази даних та моніторинг](#4-підключення-до-бази-даних-та-моніторинг)
   - [Через термінал (CLI)](#через-термінал-cli)
   - [Через GUI (MySQL Workbench / DBeaver)](#через-gui-mysql-workbench--dbeaver)
5. [Багатоетапна збірка (Multi-stage Build)](#5-багатоетапна-збірка-multi-stage-build)
6. [Шпаргалка корисних команд діагностики](#6-шпаргалка-корисних-команд-діагностики)
7. [Приклад об'єднання через Docker Compose](#7-приклад-обєднання-через-docker-compose)

---

## 1. Архітектура проекту

Проект реалізує взаємодію двох контейнерів:
1. **`mysql`**: Сервер бази даних MySQL 8.x з автоматичною ініціалізацією схеми через SQL-скрипт та постійним сховищем (Volume).
2. **`web-app`**: Вебдодаток на Flask, що підключається до MySQL за допомогою `Flask-SQLAlchemy` та `mysql-connector-python`, рахує кількість перезавантажень сторінки і зберігає стан у таблиці `counter`.

```
                    +----------------------------------------+
                    |             Docker Network             |
                    |                                        |
  Browser --------> |   [ web-app ] (Flask :8080)            |
 (localhost:8080)   |        |                               |
                    |        |  (SQLAlchemy connection)      |
                    |        v                               |
                    |   [ mysql ]   (MySQL :3306)            |
                    |        |                               |
                    +--------|-------------------------------+
                             v
                  [ Volume: /var/lib/mysql ]
```

---

## 2. Опис ключових файлів

### 📁 `Dockerfile.mysql`
Конфігурація образу бази даних MySQL:
```dockerfile
FROM mysql:latest

ENV MYSQL_ROOT_PASSWORD=1234
ENV MYSQL_DATABASE=app_db
ENV MYSQL_USER=app_user
ENV MYSQL_PASSWORD=1234

EXPOSE 3306

VOLUME /var/lib/mysql

COPY init.sql /docker-entrypoint-initdb.d/
```
- **`/docker-entrypoint-initdb.d/`**: Спеціальна директорія в офіційному образі MySQL. Будь-які `.sql` або `.sh` скрипти, скопійовані сюди, автоматично виконуються при першому запуску контейнера (якщо база ще не була ініціалізована).

### 📁 `init.sql`
Скрипт початкової ініціалізації бази даних та прав користувача:
```sql
GRANT ALL PRIVILEGES ON app_db.* TO 'app_user'@'%';

-- Use the 'app' database
USE app_db;

-- Create a table to store counter data
CREATE TABLE counter (
    id INT AUTO_INCREMENT PRIMARY KEY,
    value INT
);
```

### 📁 `Dockerfile.multistage`
Оптимізований багатоетапний білд Python-додатку:
```dockerfile
ARG PYTHON_VERSION=3.12.14

FROM python:${PYTHON_VERSION} AS base
WORKDIR /app
COPY app.py docker-logo.jpg requirements.txt ./

FROM python:${PYTHON_VERSION}-slim
WORKDIR /app
ENV MY_ENV_VAR=development
COPY --from=base /app .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8080
ENTRYPOINT [ "python", "app.py" ]
```

### 📁 `requirements.txt`
Залежності додатку:
```text
Flask==3.1.3
Flask-SQLAlchemy==3.1.1
mysql-connector-python==26.7.0
```

### 📁 `app.py`
Логіка Flask-додатку з автоматичним створенням моделі та початкового запису:
- Підключення: `mysql+mysqlconnector://app_user:1234@<HOST>/app_db`
- Автоініціалізація таблиць: `db.create_all()` всередині `with app.app_context():`
- Інкремент значення лічильника в базі при кожному запиті на `/`.

---

## 3. Покрокова інструкція запуску

### Варіант А: Рекомендований (Користувацька мережа з DNS)
У власній створеній мережі Docker контейнери можуть звертатися один до одного **за іменами** (наприклад, хост `mysql` замість динамічного IP).

1. **Створення мережі:**
   ```bash
   docker network create app-network
   ```

2. **Збірка образу MySQL:**
   ```bash
   docker build -f Dockerfile.mysql -t my-mysql:1.0 .
   ```

3. **Запуск контейнера MySQL:**
   ```bash
   docker run -d \
     --name mysql \
     --network app-network \
     -p 3306:3306 \
     -v mysql_data:/var/lib/mysql \
     my-mysql:1.0
   ```

4. **Збірка вебдодатку:**
   ```bash
   docker build -f Dockerfile.multistage -t flask-app:1.0 .
   ```

5. **Запуск вебдодатку:**
   ```bash
   docker run -d \
     --name web-app \
     --network app-network \
     -p 8080:8080 \
     flask-app:1.0
   ```

---

### Варіант Б: Запуск у дефолтній мережі bridge (за IP)

Якщо запускати контейнери без власної мережі, вони потрапляють у стандартний `bridge`, де резолв за іменами відсутній і потрібно знати IP-адресу контейнера MySQL.

1. **Запуск MySQL:**
   ```bash
   docker run -d --name mysql -p 3306:3306 my-mysql:1.0
   ```

2. **Отримання IP-адреси контейнера MySQL:**
   ```bash
   docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql
   # Наприклад, отримали 172.17.0.2
   ```

3. **Перевірка рядка підключення в `app.py`:**
   Переконайтеся, що `SQLALCHEMY_DATABASE_URI` вказує на отриманий IP (`172.17.0.2`):
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://app_user:1234@172.17.0.2/app_db'
   ```

4. **Запуск вебдодатку:**
   ```bash
   docker run -d --name web-app -p 8080:8080 flask-app:1.0
   ```

---

## 4. Підключення до бази даних та моніторинг

> [!IMPORTANT]
> **pgAdmin 4** підтримує лише **PostgreSQL** і не працює з MySQL (виникає помилка розриву з'єднання). Для MySQL використовуйте **MySQL Workbench**, **DBeaver** або термінал.

### Через термінал (CLI)
Виконати SQL-запит всередині контейнера:
```bash
docker exec -it mysql mysql -u app_user -p1234 app_db -e "SELECT * FROM counter;"
```

Увійти в інтерактивну консоль MySQL:
```bash
docker exec -it mysql mysql -u app_user -p1234 app_db
```

### Через GUI (MySQL Workbench / DBeaver)
Якщо порт `3306:3306` прокинуто на хост:
- **Hostname**: `127.0.0.1` (або IP контейнера `172.17.0.2` на Linux)
- **Port**: `3306`
- **Username**: `app_user`
- **Password**: `1234`
- **Database / Schema**: `app_db`

---

## 5. Багатоетапна збірка (Multi-stage Build)

Використання `Dockerfile.multistage` вирішує кілька ключових задач:
1. **Зменшення розміру образу**: `python:slim` займає значно менше місця, ніж повний базовий образ.
2. **Безпека та чистота**: Проміжні інструменти збірки не потрапляють у фінальний образ.
3. **Гнучкість версій через `ARG`**:
   ```bash
   docker build --build-arg PYTHON_VERSION=3.11.9 -f Dockerfile.multistage -t flask-app:3.11 .
   ```

---

## 6. Шпаргалка корисних команд діагностики

| Задача | Команда |
| :--- | :--- |
| **Переглянути логи контейнера** | `docker logs -f web-app` або `docker logs -f mysql` |
| **Перевірити мережі Docker** | `docker network ls` |
| **Деталі мережі та підключені контейнери** | `docker network inspect bridge` (або `app-network`) |
| **Дізнатися IP контейнера** | `docker inspect mysql \| grep IPAddress` |
| **Список активних томів (Volumes)** | `docker volume ls` |
| **Зупинити та видалити контейнери** | `docker stop web-app mysql && docker rm web-app mysql` |
| **Очистити невикористані ресурси** | `docker system prune` |

---

## 7. Приклад об'єднання через Docker Compose

Для ще зручнішого запуску всього стеку однією командою можна створити файл `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    build:
      context: .
      dockerfile: Dockerfile.mysql
    container_name: mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: 1234
      MYSQL_DATABASE: app_db
      MYSQL_USER: app_user
      MYSQL_PASSWORD: 1234
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - app_net

  web:
    build:
      context: .
      dockerfile: Dockerfile.multistage
    container_name: web-app
    restart: always
    environment:
      MY_ENV_VAR: production
    ports:
      - "8080:8080"
    depends_on:
      - db
    networks:
      - app_net

volumes:
  mysql_data:

networks:
  app_net:
    driver: bridge
```

Запуск всього оточення:
```bash
docker compose up -d --build
```
Зупинка:
```bash
docker compose down
```
