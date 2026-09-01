# 🐳 Docker Web Server (Flask + MySQL)

A lightweight Flask web application containerized with Docker, featuring MySQL persistence for page reload tracking, custom ASCII whale art, and a Docker logo endpoint.

---

## 🚀 Features

- **Home (`/`)**: Displays `"Docker is Awesome!"`, the value of `MY_ENV_VAR`, persistent page reload count stored in MySQL, and ASCII whale art.
- **Logo (`/logo`)**: Serves the Docker logo image (`docker-logo.jpg`).
- **Containerized**: Configured with optimized multi-stage build for Flask and a customized MySQL 8.x container with auto-initialization via `init.sql`.

---

## 📁 Project Structure

```text
.
├── app.py                  # Flask application logic & SQLAlchemy models
├── Dockerfile              # Basic Dockerfile
├── Dockerfile.multistage   # Optimized multi-stage build
├── Dockerfile.mysql        # MySQL database container build
├── init.sql                # SQL initialization schema & grants
├── requirements.txt        # Python dependencies (Flask, Flask-SQLAlchemy, MySQL)
├── docker-logo.jpg         # Docker logo image asset
├── docs/                   # Full documentation hub
│   ├── uk/                 # Ukrainian documentation
│   └── en/                 # English documentation
└── README.md               # Main project overview
```

---

## 🐳 Quick Start

### Option A: Using Docker Compose (Recommended & Easiest)
```bash
# Launch entire stack (Flask + MySQL) in detached mode
docker compose up -d

# Stop and remove containers and network
docker compose down
```

### Option B: Manual Multi-Container Setup via Docker CLI
1. **Create shared network:**
   ```bash
   docker network create app-network
   ```

2. **Launch MySQL container:**
   ```bash
   docker build -f Dockerfile.mysql -t my-mysql:1.0 .
   docker run -d --name mysql --network app-network -p 3306:3306 -v mysql_data:/var/lib/mysql my-mysql:1.0
   ```

3. **Launch Flask web application:**
   ```bash
   docker build -f Dockerfile.multistage -t flask-app:1.0 .
   docker run -d --name web-app --network app-network -p 8080:8080 flask-app:1.0
   ```

### 🌐 Access Application
- **Web UI**: [http://localhost:8080](http://localhost:8080)
- **Logo**: [http://localhost:8080/logo](http://localhost:8080/logo)

---

## 📚 Complete Documentation

- [Complete Docker Compose Guide](DOCKER_COMPOSE_GUIDE.md)
- [Docker Workflow & Architecture Guide](DOCKER_WORKFLOW_GUIDE.md)
- [Docker Command Reference & Cheat Sheet](DOCKER_CHEAT_SHEET.md)
- [Docker Best Practices & Golden Rules](DOCKER_BEST_PRACTICES.md)
