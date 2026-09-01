# 🐙 Complete Docker Compose Guide: Architecture, Specification & Multi-Container Management

This guide provides an in-depth reference for working with **Docker Compose**, detailing the modern `docker-compose.yml` specification, complete CLI command manual, case-study analysis of our project stack (Flask + MySQL), networking, volumes, environment variables, healthchecks, and troubleshooting.

---

## 📑 Table of Contents

1. [What is Docker Compose & Why Use It?](#1-what-is-docker-compose--why-use-it)
2. [Compose Evolution: V1 vs V2 & The Obsolete `version` Field](#2-compose-evolution-v1-vs-v2--the-obsolete-version-field)
3. [Anatomy & Syntax of `docker-compose.yml`](#3-anatomy--syntax-of-docker-composeyml)
   - [The `services` Key](#the-services-key)
   - [The `networks` Key](#the-networks-key)
   - [The `volumes` Key](#the-volumes-key)
   - [Environment Variables & `.env` Files](#environment-variables--env-files)
4. [Case Study: Our Project Stack (Flask + MySQL)](#4-case-study-our-project-stack-flask--mysql)
   - [Architecture Diagram](#architecture-diagram)
   - [Line-by-Line Breakdown of Current Configuration](#line-by-line-breakdown-of-current-configuration)
   - [Optimized Version with Healthcheck & .env](#optimized-version-with-healthcheck--env)
5. [Complete Docker Compose CLI Command Reference](#5-complete-docker-compose-cli-command-reference)
   - [Starting & Building](#starting--building)
   - [Monitoring & Status Inspection](#monitoring--status-inspection)
   - [Managing Containers (Stop / Start / Restart)](#managing-containers-stop--start--restart)
   - [Executing Commands Inside Services](#executing-commands-inside-services)
   - [Stopping, Teardown & Clean Up](#stopping-teardown--clean-up)
   - [Validation & Utilities](#validation--utilities)
6. [Advanced Patterns & Best Practices](#6-advanced-patterns--best-practices)
   - [Startup Synchronization with Healthchecks](#startup-synchronization-with-healthchecks)
   - [Multi-Environment Configuration (Dev / Staging / Prod) via Overrides](#multi-environment-configuration-dev--staging--prod-via-overrides)
   - [Resource Limits (CPU & RAM)](#resource-limits-cpu--ram)
   - [Security & Secrets](#security--secrets)
7. [Common Errors & Troubleshooting](#7-common-errors--troubleshooting)
8. [Quick Reference Cheat Sheet](#8-quick-reference-cheat-sheet)

---

## 1. What is Docker Compose & Why Use It?

In production and real-world architectures, applications are rarely single-container units. They typically operate as an ecosystem: web server, application backend, relational database, Redis cache, message queues (RabbitMQ/Kafka), etc.

### The Problem with Manual CLI Orchestration (`docker run`):
- You must manually create networks (`docker network create`).
- You must manually create and track persistent volumes (`docker volume create`).
- You must remember and type complex commands with dozens of arguments (`-p`, `-v`, `-e`, `--network`, `--restart`, `--name`).
- You must manually manage startup order (e.g. database must be up before backend boots).
- Hard to maintain consistency across team members and CI/CD pipelines.

### The Solution: Docker Compose
**Docker Compose** is a declarative tool for defining and running multi-container Docker applications. The entire project infrastructure and topology is documented and maintained in a single configuration file — `docker-compose.yml`.

| Metric | Docker CLI (`docker run`) | Docker Compose (`docker compose`) |
| :--- | :--- | :--- |
| **Approach** | Imperative (step-by-step commands) | Declarative (desired end-state configuration) |
| **Stack Launch** | 5-10 separate commands | Single command: `docker compose up -d` |
| **Teardown** | Manually stop and delete each container | Single command: `docker compose down` |
| **Shared Networks** | Manually created & wired to containers | Default isolated project network created automatically |
| **Reproducibility** | Subject to human error & divergent bash scripts | 100% reproducible across developer machines and servers |

---

## 2. Compose Evolution: V1 vs V2 & The Obsolete `version` Field

> [!IMPORTANT]
> **Why you see this warning:**
> `WARN[0000] docker-compose.yml: the attribute 'version' is obsolete, it will be ignored, please remove it to avoid potential confusion`

### Historical Evolution:
1. **Compose V1 (`docker-compose`)**: Written in Python as a standalone utility. Required a top-level `version: '2'`, `version: '3'`, or `version: '3.8'` string to determine the schema parser rules.
2. **Compose V2 (`docker compose`)**: Rewritten in Go and natively integrated into the Docker CLI as a subcommand (`docker compose` with a space).
3. **The Compose Specification (Current Standard)**: Unified into an open, living standard under the [Compose Specification](https://compose-spec.io/). The `version:` attribute is now formally **obsolete** and safely omitted.

### ❌ Obsolete (Compose V1 / Legacy format):
```yaml
version: '3.8'  # ⚠️ Obsolete! Triggers warnings in Compose V2

services:
  web:
    image: nginx
```

### ✅ Modern Standard (Compose Specification):
```yaml
# No version field — starts immediately with services definition
services:
  web:
    image: nginx
```

---

## 3. Anatomy & Syntax of `docker-compose.yml`

A `docker-compose.yml` file is structured using YAML. The primary top-level keys are:
- `services:` — defines containers, images, build targets, ports, environment, and dependencies.
- `networks:` — custom bridge or overlay networks for isolation and communication.
- `volumes:` — named volumes for persistent data storage across restarts.
- `configs:` / `secrets:` — sensitive data and external configuration management.

---

### The `services` Key

Each entry under `services` configures an isolated container.

```yaml
services:
  pythonapp:
    # 1. Building from a local Dockerfile
    build:
      context: .                           # Build context root
      dockerfile: Dockerfile.multistage    # Target Dockerfile
      args:                                # Build arguments (ARG)
        PYTHON_VERSION: "3.12.14"

    # 2. Image and Container Naming
    image: my-app:1.0                      # Tag for built or pulled image
    container_name: db-pythonapp           # Explicit container name

    # 3. Port Publishing (Host:Container)
    ports:
      - "8080:8080"                        # Publicly reachable via localhost:8080
      - "127.0.0.1:9000:9000"              # Bound strictly to host loopback interface

    # 4. Internal Exposing (accessible only to containers in the same network)
    expose:
      - "5000"

    # 5. Environment Variables
    environment:
      MY_ENV_VAR: development
      DATABASE_HOST: mysql                 # Other service name acts as DNS hostname
      DATABASE_PORT: 3306
    env_file:                              # Or load from an external file
      - .env

    # 6. Volumes & Bind Mounts
    volumes:
      - db-data:/var/lib/mysql             # Named volume
      - ./logs:/app/logs                   # Host directory bind mount
      - ./config.json:/app/config.json:ro  # Read-only file mount

    # 7. Networks
    networks:
      - db-data-net

    # 8. Service Dependencies & Startup Conditions
    depends_on:
      mysql:
        condition: service_healthy         # Wait until database is truly healthy

    # 9. Restart Policy
    restart: unless-stopped                # no | always | on-failure | unless-stopped

    # 10. Default Command Override
    command: ["python", "app.py", "--port", "8080"]
```

#### Restart Policies (`restart`):
- `no` (default): Never restart automatically.
- `always`: Always restart the container if it stops or upon daemon reboot.
- `on-failure`: Restart only if the container exits with a non-zero error code.
- `unless-stopped`: Always restart unless explicitly stopped by the user (`docker stop` / `docker compose stop`).

---

### The `networks` Key

Docker Compose creates a default network for your application stack (`<project_folder>_default`). All services on the same network can automatically resolve each other using service names via Docker's embedded DNS engine.

```yaml
networks:
  # Custom bridge network
  db-data-net:
    driver: bridge

  # Pre-existing external network
  shared-network:
    external: true
    name: production-network
```

---

### The `volumes` Key

Named volumes are managed directly by Docker and stored in `/var/lib/docker/volumes/`. They persist even when containers are stopped, removed, or rebuilt.

```yaml
volumes:
  # Standard local named volume
  db-data:
    driver: local

  # Pre-existing external volume
  external-volume:
    external: true
    name: shared_db_storage
```

---

### Environment Variables & `.env` Files

Compose automatically reads any `.env` file located in the project root directory and interpolates values into the YAML file:

```bash
# .env file
APP_PORT=8080
DB_ROOT_PASS=secret1234
DB_NAME=app_db
DB_USER=app_user
DB_PASS=secret1234
```

```yaml
# Usage in docker-compose.yml
services:
  pythonapp:
    ports:
      - "${APP_PORT:-8080}:8080"           # Default to 8080 if APP_PORT is unset
    environment:
      - MYSQL_PASSWORD=${DB_PASS:?Error: DB_PASS must be provided!}
```

---

## 4. Case Study: Our Project Stack (Flask + MySQL)

### Architecture Diagram

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

### Line-by-Line Breakdown of Current Configuration

Our repository `docker-compose.yml` configures two interconnected services:

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

#### Key Highlights:
1. **Network `db-data-net`**: Connects `pythonapp` and `mysql`. Through Docker DNS, Flask in `app.py` directly references the database host as `mysql`:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://app_user:1234@mysql:3306/app_db'
   ```
2. **Volume `db-data`**: Mounts persistence storage to `/var/lib/mysql`. Reload counts in the `counter` table survive container restarts.
3. **`depends_on: - mysql`**: Instructs Docker Compose to start the `db-mysql` container before starting `db-pythonapp`.

---

### Optimized Version with Healthcheck & .env

A standard `depends_on` only waits until the MySQL container starts running, not until MySQL finishes its internal schema initialization and is ready to accept queries. 

Here is the production-grade pattern with `healthcheck`:

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
    # ✅ Healthcheck probes readiness to process queries
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
    # ✅ Wait for MySQL healthcheck to pass before booting Flask
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

## 5. Complete Docker Compose CLI Command Reference

> [!TIP]
> All commands use modern Compose V2 syntax (`docker compose ...`). If you are running legacy Compose V1, use `docker-compose ...`.

### Starting & Building

```bash
# Start all services in the background (detached mode)
docker compose up -d

# Force rebuild images before starting (when Dockerfile/code changes)
docker compose up -d --build

# Start only a specific service and its dependencies
docker compose up -d pythonapp

# Force recreate containers even if configuration hasn't changed
docker compose up -d --force-recreate

# Build images without starting containers
docker compose build

# Build images from scratch ignoring cached layers
docker compose build --no-cache
```

---

### Monitoring & Status Inspection

```bash
# List running containers in the stack
docker compose ps

# List all containers (including stopped ones)
docker compose ps -a

# Follow live log streams from all services
docker compose logs -f

# Follow logs of a specific service
docker compose logs -f pythonapp

# View the last 50 log lines with timestamps
docker compose logs -f --tail=50 -t mysql

# Display running processes inside stack containers
docker compose top
```

---

### Managing Containers (Stop / Start / Restart)

```bash
# Stop running services without removing containers/networks
docker compose stop

# Start previously stopped services
docker compose start

# Restart all services in the stack
docker compose restart

# Restart a specific service (e.g. after code change)
docker compose restart pythonapp

# Pause execution of containers (SIGSTOP)
docker compose pause

# Unpause suspended containers
docker compose unpause
```

---

### Executing Commands Inside Services

```bash
# Run a command in an already running container (like docker exec)
docker compose exec pythonapp bash
docker compose exec mysql mysql -u app_user -p1234 app_db -e "SELECT * FROM counter;"

# Run a one-off task in a new container and remove it upon completion
docker compose run --rm pythonapp python -c "import app; print('App imported successfully')"
```

---

### Stopping, Teardown & Clean Up

```bash
# Stop and remove containers and networks created by compose up
docker compose down

# ⚠️ Stop and remove containers, networks, AND named volumes (resets DB!)
docker compose down -v

# Remove images built by compose
docker compose down --rmi all

# Remove orphaned containers no longer defined in the compose file
docker compose down --remove-orphans
```

---

### Validation & Utilities

```bash
# Validate syntax and view the computed configuration with interpolated variables
docker compose config

# Silent validation (returns non-zero exit code on error)
docker compose config -q
```

---

## 6. Advanced Patterns & Best Practices

### Startup Synchronization with Healthchecks
Using `condition: service_healthy` in `depends_on` eliminates race conditions between relational databases and dependent web services.

### Multi-Environment Configuration via Overrides
Docker Compose automatically merges `docker-compose.yml` with `docker-compose.override.yml` if present.

For production or CI/CD pipelines, specify files explicitly:
```bash
# Launch development environment (default override applied automatically)
docker compose up -d

# Launch production environment
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Example `docker-compose.override.yml` (for local development with live code sync):
```yaml
services:
  pythonapp:
    volumes:
      - .:/app                # Live reload: host changes immediately reflected in container
    environment:
      - FLASK_DEBUG=1
```

---

### Resource Limits (CPU & RAM)
Prevent runaway containers from starving host system resources:

```yaml
services:
  pythonapp:
    deploy:
      resources:
        limits:
          cpus: '0.50'        # Maximum 50% of a single CPU core
          memory: 512M        # Maximum 512 MB of RAM
        reservations:
          cpus: '0.10'
          memory: 128M
```

---

### Security & Secrets
- **Never commit passwords to Git**: Store sensitive values in `.env` and add it to `.dockerignore` and `.gitignore`.
- **Provide `.env.example`**: Commit a template with placeholder values to assist team onboarding.
- **Limit port exposure**: If your database is only queried internally by backend services, do not expose `ports: - "3306:3306"` publicly; use `expose: - "3306"` instead.

---

## 7. Common Errors & Troubleshooting

### 1. `WARN: the attribute 'version' is obsolete`
- **Cause**: The `version: '3'` line is present at the top of `docker-compose.yml`.
- **Fix**: Remove the `version:` line. The modern Compose V2 engine uses the open Compose Specification.

### 2. `Bind for 0.0.0.0:8080 failed: port is already allocated`
- **Cause**: Port 8080 or 3306 is already bound by another process or standalone container.
- **Fix**:
  - Identify running process: `sudo lsof -i :8080` or `sudo netstat -tulpn | grep 8080`
  - Rebind to another host port in `docker-compose.yml`: `ports: - "8081:8080"`.

### 3. `mysql.connector.errors.DatabaseError: 2003: Can't connect to MySQL server`
- **Cause**: The Flask web app attempted to connect before the MySQL server completed initialization, or the hostname is invalid.
- **Fix**:
  - Verify that the hostname matches the service name: `@mysql:3306` (or `db-mysql`).
  - Add a `healthcheck` block to `mysql` and `condition: service_healthy` to `pythonapp.depends_on`.

### 4. Schema changes in `init.sql` are ignored after restart
- **Cause**: Scripts in `/docker-entrypoint-initdb.d/` execute **only once** when the database volume directory is empty.
- **Fix**: Rebuild with volume deletion to re-run the initialization schema:
  ```bash
  docker compose down -v
  docker compose up -d --build
  ```

### 5. `Found orphan containers` warning
- **Cause**: Services previously declared in `docker-compose.yml` were removed or renamed while their containers remained running.
- **Fix**: Clean them up with the cleanup flag:
  ```bash
  docker compose up -d --remove-orphans
  ```

---

## 8. Quick Reference Cheat Sheet

| Task | Command |
| :--- | :--- |
| **Start stack in background** | `docker compose up -d` |
| **Rebuild images and start** | `docker compose up -d --build` |
| **List stack container status** | `docker compose ps` |
| **Stream real-time logs** | `docker compose logs -f` |
| **Stream single service logs** | `docker compose logs -f pythonapp` |
| **Stop stack (preserve state)** | `docker compose stop` |
| **Start stopped stack** | `docker compose start` |
| **Restart single service** | `docker compose restart pythonapp` |
| **Execute command in container** | `docker compose exec pythonapp bash` |
| **Stop and remove containers/networks** | `docker compose down` |
| **Full teardown with volumes (DB purge)** | `docker compose down -v` |
| **Validate and render configuration** | `docker compose config` |
