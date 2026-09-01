# 🐳 Docker Web Server (Flask + MySQL)

A lightweight Flask web application containerized with Docker, featuring MySQL persistence for page reload tracking, custom ASCII whale art, and a Docker logo endpoint.

---

## 🚀 Features

- **Home (`/`)**: Displays `"Docker is Awesome!"`, `MY_ENV_VAR`, page reload counter stored in MySQL, and ASCII whale art.
- **Logo (`/logo`)**: Serves the Docker logo image (`docker-logo.jpg`).
- **Containerized**: Configured with multi-stage builds and containerized MySQL database with automated schema initialization.

---

## 📁 Project Structure

```text
.
├── app.py                  # Flask application logic & SQLAlchemy models
├── Dockerfile              # Basic Dockerfile
├── Dockerfile.multistage   # Multi-stage optimized Dockerfile
├── Dockerfile.mysql        # MySQL database container build
├── init.sql                # SQL initialization schema & grants
├── requirements.txt        # Python dependencies
├── docker-logo.jpg         # Docker logo asset
├── docs/                   # Complete documentation
│   ├── uk/                 # 🇺🇦 Українська документація
│   └── en/                 # 🇬🇧 English Documentation
└── README.md               # Main repository documentation
```

---

## 📚 Documentation / Документація

All project guides, cheat sheets, and best practices are organized by language in the [`docs/`](docs/) directory:

| 🇺🇦 Українська (Ukrainian) | 🇬🇧 English |
| :--- | :--- |
| 🐙 [Повний посібник по Docker Compose](docs/uk/DOCKER_COMPOSE_GUIDE.md) | 🐙 [Complete Docker Compose Guide](docs/en/DOCKER_COMPOSE_GUIDE.md) |
| 📖 [Посібник по роботі з Docker](docs/uk/DOCKER_WORKFLOW_GUIDE.md) | 📖 [Docker Workflow Guide](docs/en/DOCKER_WORKFLOW_GUIDE.md) |
| ⚡ [Шпаргалка команд Docker](docs/uk/DOCKER_CHEAT_SHEET.md) | ⚡ [Docker Cheat Sheet](docs/en/DOCKER_CHEAT_SHEET.md) |
| 🛡️ [Найкращі практики та правила](docs/uk/DOCKER_BEST_PRACTICES.md) | 🛡️ [Docker Best Practices](docs/en/DOCKER_BEST_PRACTICES.md) |
| 📄 [Опис проєкту (UA)](docs/uk/README.md) | 📄 [Project Overview (EN)](docs/en/README.md) |

---

## 🐳 Quick Start

### Option A: Using Docker Compose (Recommended)
```bash
# Start entire stack (Flask + MySQL) in detached mode
docker compose up -d

# Stop and tear down stack
docker compose down
```

### Option B: Manual Multi-Container Setup (Docker CLI)

1. **Create network:**
   ```bash
   docker network create app-network
   ```

2. **Start MySQL container:**
   ```bash
   docker build -f Dockerfile.mysql -t my-mysql:1.0 .
   docker run -d --name mysql --network app-network -p 3306:3306 -v mysql_data:/var/lib/mysql my-mysql:1.0
   ```

3. **Start Flask application container:**
   ```bash
   docker build -f Dockerfile.multistage -t flask-app:1.0 .
   docker run -d --name web-app --network app-network -p 8080:8080 flask-app:1.0
   ```

4. **Open in browser**: [http://localhost:8080](http://localhost:8080)
