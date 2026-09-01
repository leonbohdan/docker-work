# 🐳 Docker Ultimate Reference Guide & Cheat Sheet

A comprehensive reference for Dockerfile directives, image build & management, container lifecycle commands, volume persistence, networking, monitoring, and Docker Compose.

---

## 📑 Table of Contents
1. [Dockerfile: Instructions & Architecture](#1-dockerfile-instructions--architecture)
2. [Image Building & Management](#2-image-building--management)
3. [Container Lifecycle & Execution](#3-container-lifecycle--execution)
4. [Debugging, Monitoring & Exec](#4-debugging-monitoring--exec)
5. [Data Persistence: Volumes & Bind Mounts](#5-data-persistence-volumes--bind-mounts)
6. [Docker Networking](#6-docker-networking)
7. [System Cleanup & Maintenance](#7-system-cleanup--maintenance)
8. [Docker Compose Basics](#8-docker-compose-basics)
9. [Best Practices & Pro Tips](#9-best-practices--pro-tips)

---

## 1. Dockerfile: Instructions & Architecture

A `Dockerfile` is an automated build script for creating container images. Each line creates a read-only layer in the image's filesystem.

### 📋 Directives Reference

| Directive | Description | Example |
| :--- | :--- | :--- |
| `FROM` | Base image to build upon (must be 1st instruction) | `FROM python:3.11-slim` |
| `WORKDIR` | Sets the working directory inside the container | `WORKDIR /app` |
| `COPY` | Copies local files/directories into container | `COPY requirements.txt .` |
| `ADD` | Copies files; auto-extracts `.tar` & supports URLs | `ADD app.tar.gz /app/` |
| `RUN` | Executes commands during build time (creates a layer) | `RUN pip install -r requirements.txt` |
| `ENV` | Sets persistent environment variables | `ENV PORT=8080 ENV=production` |
| `ARG` | Variables available **only** during build time | `ARG APP_VERSION=1.0.0` |
| `EXPOSE` | Informs Docker of runtime port listening (documentation only) | `EXPOSE 8080` |
| `USER` | Sets non-root user UID/name for commands | `USER appuser` |
| `VOLUME` | Creates a mount point for external data persistence | `VOLUME ["/app/data"]` |
| `ENTRYPOINT` | Default executable process (hard to override) | `ENTRYPOINT ["python", "app.py"]` |
| `CMD` | Default arguments for `ENTRYPOINT` or fallback command | `CMD ["--port", "8080"]` |
| `HEALTHCHECK`| Instruction to test container health periodically | `HEALTHCHECK --interval=30s CMD curl -f http://localhost:8080/ \|\| exit 1` |

---

### 🔍 Key Differences to Know

#### 1. `CMD` vs `ENTRYPOINT`
- **`ENTRYPOINT`** defines the fixed binary executable.
- **`CMD`** provides default parameters that can easily be overridden at runtime via `docker run`.
- **Recommended format (Exec Form)**: Always use the JSON array syntax `["executable", "param1", "param2"]` to avoid spawning an unnecessary shell (`/bin/sh -c`) and ensure proper POSIX signal propagation (SIGTERM).

```dockerfile
ENTRYPOINT ["python", "app.py"]
CMD ["--host", "0.0.0.0", "--port", "8080"]
```
> Running `docker run my-image --port 9000` overrides the `CMD` portion with `--port 9000`.

#### 2. `COPY` vs `ADD`
- **Prefer `COPY`** for general file copying.
- Only use `ADD` when you explicitly need automatic local `.tar` extraction into the container.

#### 3. Multi-Stage Builds
Allows building lightweight production images by separating build tools from the final runtime environment:

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
Excludes unnecessary files from the Docker build context (speeds up builds and reduces image footprint):
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

## 2. Image Building & Management

### 🔨 Building Custom Images

```bash
# Build image from current directory (with name:tag)
docker build -t my-app:1.0 .

# Build from specific Dockerfile
docker build -f Dockerfile.multistage -t my-app:multistage .

# Clean build without cache
docker build --no-cache -t my-app:1.0 .

# Pass build-time arguments (ARG)
docker build --build-arg APP_VERSION=2.0.0 -t my-app:2.0.0 .

# Build a specific target stage in a multi-stage Dockerfile
docker build --target builder -t my-app:builder .
```

### 📦 Managing Images

```bash
# List local images
docker images
# or
docker image ls

# Tag an existing image
docker tag my-app:1.0 myusername/my-app:1.0

# Remove an image
docker rmi my-app:1.0

# Force remove an image
docker rmi -f my-app:1.0

# Remove dangling (<none>) images
docker image prune

# Remove ALL unused images
docker image prune -a

# View image layer history
docker history my-app:1.0

# Export image to tar archive (for offline distribution)
docker save -o my-app.tar my-app:1.0

# Load image from tar archive
docker load -i my-app.tar

# Push image to registry / Docker Hub
docker push myusername/my-app:1.0

# Pull image from registry
docker pull python:3.11-slim
```

---

## 3. Container Lifecycle & Execution

### 🚀 Running Containers (`docker run`)

```bash
# 1. Full production-ready web server run:
docker run -d \
  --name web-app \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -e ENV=production \
  --restart unless-stopped \
  my-app:1.0

# 2. Interactive container for debugging:
docker run -it --rm --name debug-container python:3.11-slim /bin/bash
```

#### 🔑 Essential `docker run` Flags:

| Flag | Description |
| :--- | :--- |
| `-d` (`--detach`) | Run container in background (detached mode) |
| `-it` | Interactive mode + allocate pseudo-TTY (for bash/sh) |
| `--name <name>` | Assign a friendly name to the container |
| `-p <host>:<cont>` | Publish port: `<host_port>:<container_port>` |
| `-v <host>:<cont>` | Mount volume or host directory into container |
| `-e KEY=VAL` | Set environment variable |
| `--env-file <file>` | Read environment variables from a file |
| `--rm` | Automatically remove container when it exits |
| `--restart <policy>`| Restart policy (`no`, `always`, `unless-stopped`, `on-failure`) |
| `--network <net>` | Connect container to a specific network |
| `-m 512m` | Limit memory usage |
| `--cpus="1.5"` | Limit CPU usage |

---

### 🕹️ Managing Container State

```bash
# List only running containers
docker ps

# List ALL containers (running and stopped)
docker ps -a

# Stop a container gracefully (SIGTERM -> SIGKILL after 10s)
docker stop web-app

# Kill container immediately (SIGKILL)
docker kill web-app

# Start a stopped container
docker start web-app

# Restart a container
docker restart web-app

# Pause all container processes (freeze)
docker pause web-app

# Resume container processes
docker unpause web-app

# Remove a stopped container
docker rm web-app

# Force stop and remove container in one step
docker rm -f web-app

# Remove all stopped containers
docker container prune
```

---

## 4. Debugging, Monitoring & Exec

```bash
# View container logs
docker logs web-app

# Stream logs in real-time + show last 100 lines
docker logs -f --tail 100 web-app

# Execute interactive shell inside running container
docker exec -it web-app /bin/bash
# or (for Alpine/minimal images):
docker exec -it web-app /bin/sh

# Run a one-off command inside container
docker exec web-app ls -la /app

# Copy file from host into container
docker cp ./config.json web-app:/app/config.json

# Copy file from container to host
docker cp web-app:/app/logs.txt ./logs.txt

# Detailed JSON metadata inspection
docker inspect web-app

# Extract container IP address using format filter
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' web-app

# Live resource usage metrics (CPU, RAM, Network I/O)
docker stats

# List running processes inside container
docker top web-app

# Inspect filesystem changes compared to image
docker diff web-app
```

---

## 5. Data Persistence: Volumes & Bind Mounts

Containers have ephemeral storage by default — once removed, changes are lost. Use **Volumes** or **Bind Mounts** for persistence.

```
Host Machine                             Container
┌────────────────────────────────┐       ┌────────────────────────────┐
│ /var/lib/docker/volumes/my-vol │ ────> │ /app/data  (Named Volume)  │
│ /home/user/project/src         │ ────> │ /app/src   (Bind Mount)    │
└────────────────────────────────┘       └────────────────────────────┘
```

### 📁 1. Named Volumes (Docker-managed — recommended for databases)

```bash
# Create a volume
docker volume create app_data

# List volumes
docker volume ls

# Inspect volume details
docker volume inspect app_data

# Mount named volume in docker run
docker run -d --name db -v app_data:/var/lib/mysql mysql:8.0

# Remove volume
docker volume rm app_data

# Remove all unused volumes
docker volume prune
```

### 📂 2. Bind Mounts (Mount host directory directly — great for development)

```bash
# Mount current directory into /app (Hot reload / dev)
docker run -d -p 8080:8080 -v $(pwd):/app --name dev-server my-app:1.0
```

---

## 6. Docker Networking

Containers run on the default `bridge` network by default. Create user-defined networks for secure container communication via **DNS hostnames**.

```bash
# Create custom bridge network
docker network create my-network

# List networks
docker network ls

# Run containers on the same network
docker run -d --name database --network my-network mysql:8.0
docker run -d --name web --network my-network -p 8080:8080 my-app:1.0
# 'web' can now reach MySQL using hostname 'database'!

# Connect running container to network
docker network connect my-network other-container

# Disconnect container from network
docker network disconnect my-network other-container

# Inspect network details and connected containers
docker network inspect my-network

# Remove network
docker network rm my-network

# Remove all unused networks
docker network prune
```

---

## 7. System Cleanup & Maintenance

When reclaiming disk space:

```bash
# Show Docker disk usage summary
docker system df

# Verbose disk usage breakdown
docker system df -v

# Standard cleanup: stopped containers, dangling images, unused networks
docker system prune

# Deep cleanup: ALL stopped containers, unused networks, volumes, and unused images
docker system prune -a --volumes
```

---

## 8. Docker Compose Basics

Multi-container applications are defined and orchestrated with `docker compose` using `docker-compose.yml`.

### Example `docker-compose.yml`:
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

### ⚡ Compose Commands Cheat Sheet:

```bash
# Start all services detached (and build if needed)
docker compose up -d

# Force rebuild images before starting
docker compose up -d --build

# Check status of compose services
docker compose ps

# Live streaming logs of all services
docker compose logs -f

# Logs for a specific service
docker compose logs -f web

# Stop and remove containers and networks
docker compose down

# Stop and remove everything INCLUDING volumes
docker compose down -v

# Execute command inside a service container
docker compose exec web /bin/sh
```

---

## 9. Best Practices & Pro Tips

1. **Layer Caching**:
   - Place infrequently changed instructions (copying `requirements.txt` and installing dependencies) **before** copying volatile application source code (`COPY . .`).
2. **Minimize Layers**:
   - Chain related commands using `&&` and clear package manager caches within the same `RUN` layer:
     ```dockerfile
     RUN apt-get update && apt-get install -y --no-install-recommends \
         curl \
         ca-certificates \
         && rm -rf /var/lib/apt/lists/*
     ```
3. **Security**:
   - Do not run processes as `root`. Create and switch to a non-privileged `USER`.
   - Never hardcode passwords or API keys in `Dockerfile` or `ENV`.
4. **Use Minimal Base Images**:
   - Favor `alpine` or `slim` images (e.g. `python:3.11-slim` over full `python:3.11`).
5. **Pin Specific Versions**:
   - Avoid mutable `:latest` tags in production. Specify exact tags like `python:3.12.14-slim`.
6. **Always Maintain `.dockerignore`**:
   - Prevent secrets, `.venv`, `node_modules`, and build artifacts from leaking into images.
