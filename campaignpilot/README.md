# campaignpilot-ai

A FastAPI service skeleton for campaign automation workflows with explicit dependency injection, structured logging, and consistent error handling.

## What Changed

- **Dependency injection** via an `AppContainer` stored on `app.state` and accessed through FastAPI dependencies.
- **Improved logging** with structured JSON logs and request-level context (`request_id`, `path`, `method`).
- **Improved error handling** with custom application exceptions and centralized exception handlers.
- **Better folder separation** by splitting app bootstrap, dependency providers, routes, and error modules.
- **Basic unit tests** for health route, error contract, and settings behavior.

## Project Structure

```text
campaignpilot/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   └── system.py
│   │   └── router.py
│   ├── bootstrap/
│   │   └── middleware.py
│   ├── core/
│   │   ├── config.py
│   │   ├── container.py
│   │   ├── database.py
│   │   └── logging.py
│   ├── dependencies/
│   │   └── providers.py
│   ├── errors/
│   │   ├── exceptions.py
│   │   └── handlers.py
│   ├── application.py
│   └── main.py
├── tests/
│   └── unit/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Setup Instructions

### 1. Configure environment

```bash
cp .env.example .env
```

Edit `.env` values as needed.

### 2. Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the app

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs:

- http://localhost:8000/docs
- http://localhost:8000/redoc

### 4. Run tests

```bash
pytest
```

## Docker

```bash
docker compose up --build
```
