# 🐳 Вебсервер у Docker (Flask + MySQL)

Легкий вебдодаток на Flask, контейнеризований за допомогою Docker, з базою даних MySQL, персистентним лічильником відвідувань, ASCII-артом кита та маршрутом для логотипу.

---

## 🚀 Функціонал

- **Головна (`/`)**: Виводить повідомлення `"Docker is Awesome!"`, значення змінної середовища `MY_ENV_VAR`, кількість перезавантажень сторінки (збережених у базі даних MySQL) та ASCII-арт кита.
- **Логотип (`/logo`)**: Віддає зображення логотипу Docker (`docker-logo.jpg`).
- **Контейнеризація**: Повністю налаштована багатоетапна збірка (Multi-stage build) для Flask та контейнер MySQL 8.x з автоініціалізацією через `init.sql`.

---

## 📁 Структура Проєкту

```text
.
├── app.py                  # Основний код вебдодатку на Flask з SQLAlchemy
├── Dockerfile              # Базовий Dockerfile
├── Dockerfile.multistage   # Оптимізована багатоетапна збірка
├── Dockerfile.mysql        # Dockerfile для бази даних MySQL
├── init.sql                # SQL-скрипт ініціалізації бази та таблиць
├── requirements.txt        # Залежності Python (Flask, Flask-SQLAlchemy, MySQL)
├── docker-logo.jpg         # Зображення логотипу
├── docs/                   # Повна документація проєкту
│   ├── uk/                 # Документація українською мовою
│   └── en/                 # Документація англійською мовою
└── README.md               # Головний опис проєкту
```

---

## 🐳 Швидкий запуск

### Варіант А: Через Docker Compose (Найпростіший спосіб)
```bash
# Запуск усього стеку (Flask + MySQL) у фоновому режимі
docker compose up -d

# Зупинка та видалення контейнерів і мережі
docker compose down
```

### Варіант Б: Вручну через Docker CLI
1. **Створення спільної мережі:**
   ```bash
   docker network create app-network
   ```

2. **Запуск контейнера MySQL:**
   ```bash
   docker build -f Dockerfile.mysql -t my-mysql:1.0 .
   docker run -d --name mysql --network app-network -p 3306:3306 -v mysql_data:/var/lib/mysql my-mysql:1.0
   ```

3. **Запуск вебдодатку:**
   ```bash
   docker build -f Dockerfile.multistage -t flask-app:1.0 .
   docker run -d --name web-app --network app-network -p 8080:8080 flask-app:1.0
   ```

### 🌐 Доступ до додатку
- **Вебінтерфейс**: [http://localhost:8080](http://localhost:8080)
- **Логотип**: [http://localhost:8080/logo](http://localhost:8080/logo)

---

## 📚 Детальна документація

- [Повний посібник по Docker Compose](DOCKER_COMPOSE_GUIDE.md)
- [Посібник по роботі з Docker та архітектурою](DOCKER_WORKFLOW_GUIDE.md)
- [Шпаргалка команд Docker (Cheat Sheet)](DOCKER_CHEAT_SHEET.md)
- [Найкращі практики та правила Docker](DOCKER_BEST_PRACTICES.md)
