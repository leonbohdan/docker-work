# 🐳 Docker Workflow Guide: Flask + MySQL + Multi-Container Architecture

This document details the project's container architecture, multi-container communication principles (Flask App + MySQL), multi-stage builds, networking, persistent volumes, and client connectivity (CLI / MySQL Workbench).

---

## 📑 Table of Contents
1. [Project Architecture](#1-project-architecture)
2. [Key Files Overview](#2-key-files-overview)
3. [Step-by-Step Launch Guide](#3-step-by-step-launch-guide)
   - [Option A: Recommended (Custom Network with DNS Resolution)](#option-a-recommended-custom-network-with-dns-resolution)
   - [Option B: Default Bridge Network (by IP Address)](#option-b-default-bridge-network-by-ip-address)
4. [Database Connection & Monitoring](#4-database-connection--monitoring)
   - [Terminal / CLI](#terminal--cli)
   - [GUI Clients (MySQL Workbench / DBeaver)](#gui-clients-mysql-workbench--dbeaver)
5. [Multi-Stage Builds](#5-multi-stage-builds)
6. [Troubleshooting & Diagnostics Cheat Sheet](#6-troubleshooting--diagnostics-cheat-sheet)
7. [Docker Compose Integration](#7-docker-compose-integration)

---

## 1. Project Architecture

The project consists of two interacting containers:
1. **`mysql`**: MySQL 8.x database server with automated schema initialization via an SQL script and persistent storage (Volume).
2. **`web-app`**: Flask web application connected to MySQL via `Flask-SQLAlchemy` and `mysql-connector-python`, tracking page reloads in a persistent `counter` table.

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

## 2. Key Files Overview

### 📁 `Dockerfile.mysql`
Configuration for building the MySQL database container:
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
- **`/docker-entrypoint-initdb.d/`**: A special directory in the official MySQL image. Any `.sql` or `.sh` scripts placed here are executed automatically during the container's first run (when the data volume is initialized).

### 📁 `init.sql`
Initial database setup script configuring grants and schema:
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
Optimized multi-stage Dockerfile for the Python application:
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
Application dependencies:
```text
Flask==3.1.3
Flask-SQLAlchemy==3.1.1
mysql-connector-python==26.7.0
```

### 📁 `app.py`
Flask application logic with automatic table and initial record creation:
- Database URI: `mysql+mysqlconnector://app_user:1234@<HOST>/app_db`
- Auto schema creation: `db.create_all()` inside `with app.app_context():`
- Counter increments on each request to `/`.

---

## 3. Step-by-Step Launch Guide

### Option A: Recommended (Custom Network with DNS Resolution)
In a user-defined Docker bridge network, containers can discover and reach each other **by container name** (e.g., hostname `mysql` instead of dynamic IP addresses).

1. **Create the network:**
   ```bash
   docker network create app-network
   ```

2. **Build MySQL image:**
   ```bash
   docker build -f Dockerfile.mysql -t my-mysql:1.0 .
   ```

3. **Start MySQL container:**
   ```bash
   docker run -d \
     --name mysql \
     --network app-network \
     -p 3306:3306 \
     -v mysql_data:/var/lib/mysql \
     my-mysql:1.0
   ```

4. **Build Flask application image:**
   ```bash
   docker build -f Dockerfile.multistage -t flask-app:1.0 .
   ```

5. **Start Flask application container:**
   ```bash
   docker run -d \
     --name web-app \
     --network app-network \
     -p 8080:8080 \
     flask-app:1.0
   ```

---

### Option B: Default Bridge Network (by IP Address)

If running containers without a custom network, they join the default `bridge` network where automatic DNS resolution by name is unavailable, requiring container IP lookup.

1. **Start MySQL:**
   ```bash
   docker run -d --name mysql -p 3306:3306 my-mysql:1.0
   ```

2. **Get the MySQL container IP address:**
   ```bash
   docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql
   # e.g., output: 172.17.0.2
   ```

3. **Ensure connection string in `app.py` points to that IP:**
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://app_user:1234@172.17.0.2/app_db'
   ```

4. **Start the Flask web container:**
   ```bash
   docker run -d --name web-app -p 8080:8080 flask-app:1.0
   ```

---

## 4. Database Connection & Monitoring

> [!IMPORTANT]
> **pgAdmin 4** only supports **PostgreSQL** protocol and will fail to connect to MySQL (`server closed the connection unexpectedly`). Use **MySQL Workbench**, **DBeaver**, or the CLI for MySQL.

### Terminal / CLI
Execute a query directly inside the running container:
```bash
docker exec -it mysql mysql -u app_user -p1234 app_db -e "SELECT * FROM counter;"
```

Open an interactive MySQL shell:
```bash
docker exec -it mysql mysql -u app_user -p1234 app_db
```

### GUI Clients (MySQL Workbench / DBeaver)
With port `3306:3306` mapped to host:
- **Hostname**: `127.0.0.1` (or container IP `172.17.0.2` on Linux)
- **Port**: `3306`
- **Username**: `app_user`
- **Password**: `1234`
- **Database / Schema**: `app_db`

---

## 5. Multi-Stage Builds

Using `Dockerfile.multistage` offers several advantages:
1. **Minimized Image Size**: `python:slim` consumes significantly less disk space than the full Python image.
2. **Security & Cleanliness**: Intermediate build utilities are excluded from the runtime image.
3. **Flexible Versioning with `ARG`**:
   ```bash
   docker build --build-arg PYTHON_VERSION=3.11.9 -f Dockerfile.multistage -t flask-app:3.11 .
   ```

---

## 6. Troubleshooting & Diagnostics Cheat Sheet

| Task | Command |
| :--- | :--- |
| **Inspect container logs** | `docker logs -f web-app` or `docker logs -f mysql` |
| **List Docker networks** | `docker network ls` |
| **Inspect network and attached containers** | `docker network inspect bridge` (or `app-network`) |
| **Find container IP address** | `docker inspect mysql \| grep IPAddress` |
| **List Docker volumes** | `docker volume ls` |
| **Stop and remove containers** | `docker stop web-app mysql && docker rm web-app mysql` |
| **Prune unused resources** | `docker system prune` |

---

## 7. Docker Compose Integration

To orchestrate the entire multi-container stack with a single command, use `docker-compose.yml`:

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

Start the stack:
```bash
docker compose up -d --build
```
Stop the stack:
```bash
docker compose down
```
