# 🛡️ Docker Golden Rules & Best Practices Guide

This document presents 10 essential rules with practical examples (❌ Bad Practice vs ✅ Good Practice), along with bonus security and optimization guidelines.

---

## 📑 Table of Contents
1. [Rule 01: Use Official Images](#-rule-01-use-official-images)
2. [Rule 02: Don't Ever Use Tag :latest in Production](#-rule-02-dont-ever-use-tag-latest-in-production)
3. [Rule 03: Use Smallest Possible Base Image](#-rule-03-use-smallest-possible-base-image)
4. [Rule 04: Don't Install Unnecessary Packages](#-rule-04-dont-install-unnecessary-packages)
5. [Rule 05: Use Multi-Stage Builds](#-rule-05-use-multi-stage-builds)
6. [Rule 06: Each Container Should Run Only One Application](#-rule-06-each-container-should-run-only-one-application)
7. [Rule 07: Leverage Layer Caching Properly](#-rule-07-leverage-layer-caching-properly)
8. [Rule 08: Split Long RUN Commands into Readable Chunks](#-rule-08-split-long-run-commands-into-readable-chunks)
9. [Rule 09: Prefer COPY over ADD](#-rule-09-prefer-copy-over-add)
10. [Rule 10: ALWAYS Use WORKDIR](#-rule-10-always-use-workdir)
11. [⭐ Bonus Critical Rules](#-bonus-critical-rules)

---

## 📌 Rule 01: Use Official Images

- **Why it matters:** Official Docker Hub images are maintained by dedicated teams, regularly patched for security vulnerabilities, and follow industry best practices.

```dockerfile
# ❌ Bad: Unknown third-party user image (security risk)
FROM randomuser123/python-flask:latest

# ✅ Good: Official verified image
FROM python:3.11-slim
```

---

## 📌 Rule 02: Don't Ever Use Tag `:latest` in Production

- **Why it matters:** The `:latest` tag is mutable and points to the newest release, which can introduce breaking changes unexpectedly. It prevents reproducible builds and complicates rollbacks.

```dockerfile
# ❌ Bad: Unpredictable, version may change unexpectedly
FROM node:latest
FROM postgres:latest

# ✅ Good: Deterministic pinned version
FROM node:20.11.0-alpine
FROM postgres:15.6-alpine
```

---

## 📌 Rule 03: Use Smallest Possible Base Image

- **Why it matters:** Smaller base images reduce build times, network transfer times (`docker pull`/`push`), disk usage, and minimize attack surfaces (fewer packages = fewer CVEs).

| Image | Approximate Size | Purpose |
| :--- | :--- | :--- |
| `python:3.11` (Full) | ~1000 MB | Full development environment with build tools |
| `python:3.11-slim` | ~120 MB | Minimal Debian + Python runtime |
| `python:3.11-alpine` | ~50 MB | Ultra-lightweight Alpine Linux based on musl libc |

```dockerfile
# ❌ Bad: Bloated with 900+ MB of unnecessary tools
FROM python:3.11

# ✅ Good: Lightweight, secure, and fast
FROM python:3.11-slim
```

---

## 📌 Rule 04: Don't Install Unnecessary Packages

- **Why it matters:** Avoid installing editors (`vim`, `nano`), build tools, or debug packages into final production images. Always use `--no-install-recommends` and clean package caches.

```dockerfile
# ❌ Bad: Installs unnecessary recommended packages and leaves cache on disk
RUN apt-get update && apt-get install -y curl vim git wget

# ✅ Good: Installs only required packages and purges package lists
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
```

---

## 📌 Rule 05: Use Multi-Stage Builds

- **Why it matters:** Multi-stage builds keep compilation tools, intermediate files, and dev-dependencies out of the production runtime image.

```dockerfile
# --- Stage 1: Build Stage ---
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# --- Stage 2: Production Stage ---
FROM python:3.11-slim
WORKDIR /app
# Copy only artifacts from builder
COPY --from=builder /root/.local /root/.local
COPY . /app
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8080
CMD ["python", "app.py"]
```

---

## 📌 Rule 06: Each Container Should Run Only One Application

- **Why it matters:** Running one process per container ensures decoupled lifecycles, clear logging, independent horizontal scaling, and proper POSIX signal handling (PID 1).

```
❌ Bad:
┌──────────────────────────────────────┐
│  Container: Web App + Postgres + SSH │
└──────────────────────────────────────┘

✅ Good (Docker Compose / Network):
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│  Container 1   │ <-> │  Container 2   │ <-> │  Container 3   │
│   (Web App)    │     │  (PostgreSQL)  │     │    (Redis)     │
└────────────────┘     └────────────────┘     └────────────────┘
```

---

## 📌 Rule 07: Leverage Layer Caching Properly

- **Why it matters:** Docker caches layers sequentially. Order directives from least frequently changed (dependencies) to most frequently changed (source code) to speed up builds.

```dockerfile
# ❌ Bad: Any change in app.py invalidates cache and reinstalls all packages
COPY . /app
RUN pip install -r requirements.txt

# ✅ Good: Dependencies are cached and only rebuilt when requirements change
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
```

---

## 📌 Rule 08: Split Long RUN Commands into Readable Chunks

- **Why it matters:** Group related commands into a single `RUN` layer using `&& \` to avoid creating unnecessary intermediate layers and make the Dockerfile readable.

```dockerfile
# ❌ Bad: Creates 4 separate layers; temporary files remain in history
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git
RUN rm -rf /var/lib/apt/lists/*

# ✅ Good: Single layer, clean history, cache cleared in the same layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
```

---

## 📌 Rule 09: Prefer COPY over ADD

- **Why it matters:** `COPY` is explicit, safe, and transparent. `ADD` has implicit behavior (auto-tar extraction and URL fetching). Only use `ADD` when you specifically need local tar auto-extraction.

```dockerfile
# ❌ Bad: Ambiguous behavior for simple files
ADD requirements.txt /app/
ADD app.py /app/

# ✅ Good: Explicit, clear, and predictable
COPY requirements.txt /app/
COPY app.py /app/

# 💡 Valid use case for ADD: Auto-extracting tarball
ADD release-v1.0.tar.gz /app/
```

---

## 📌 Rule 10: ALWAYS Use WORKDIR

- **Why it matters:** Never rely on default base image working directories. Never use `RUN cd /app` (it does not persist across layers!). `WORKDIR` safely creates and sets the path for all subsequent instructions.

```dockerfile
# ❌ Bad: 'cd' only applies to this single RUN line and is lost on next line
RUN mkdir /app
RUN cd /app
COPY app.py . # File lands in root or default directory instead of /app!

# ✅ Good: Creates directory and sets persistent context
WORKDIR /app
COPY app.py .
```

---

## ⭐ Bonus Critical Rules

### 🔒 11. Run as Non-Root USER
Containers execute as `root` by default. If a container is compromised, the attacker may gain access to the host.
```dockerfile
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser
```

### 🙈 12. Always Maintain `.dockerignore`
Prevents secrets, `.venv`, `node_modules`, `.git` histories, and temporary files from leaking into the container build context.

### 🔑 13. Never Hardcode Secrets in Dockerfile
Use environment variables passed at runtime (`docker run -e ...` / `--env-file`) or Docker Secrets.

### ⚡ 14. Use JSON Exec Form for CMD & ENTRYPOINT
```dockerfile
# ❌ Shell Form: wrapped in /bin/sh -c (signals like SIGTERM are blocked)
CMD python app.py

# ✅ Exec Form: executed directly (container stops immediately and cleanly)
CMD ["python", "app.py"]
```
