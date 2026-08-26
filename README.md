# Docker Web Server

A lightweight Flask web application containerized with Docker, featuring ASCII art and a Docker logo endpoint.

---

## 🚀 Features

- **Home (`/`)**: Displays a custom Docker whale ASCII art along with the message `"Docker is Awesome!"`.
- **Logo (`/logo`)**: Serves the Docker logo image (`docker-logo.jpg`).
- **Containerized**: Fully configured to build and run with Docker on port `8080`.

---

## 📁 Project Structure

```text
.
├── app.py              # Flask application logic & routes
├── Dockerfile          # Docker configuration for containerization
├── docker-logo.jpg     # Docker logo image asset
└── README.md           # Project documentation
```

---

## 🐳 Running with Docker

### 1. Build the Docker Image

```bash
docker build -t server:1.0 .
```

### 2. Run the Docker Container

```bash
docker run -d --name web-server -p 8080:8080 server:1.0
```

### 3. Access the Application

- **Web UI**: Open [http://localhost:8080](http://localhost:8080) in your browser.
- **Logo Endpoint**: Open [http://localhost:8080/logo](http://localhost:8080/logo).

### 4. Stop and Remove Container

```bash
docker stop web-server
docker rm web-server
```

---

## 💻 Running Locally (Without Docker)

### Prerequisites

- Python 3.10+
- `pip` / `venv`

### Setup & Run

1. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install Flask
   ```

3. **Start the Flask server:**
   ```bash
   python app.py
   ```

4. The application will be available at [http://localhost:8080](http://localhost:8080).
