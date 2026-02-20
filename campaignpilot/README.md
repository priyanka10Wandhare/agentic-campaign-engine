# campaignpilot-ai

Production-structured FastAPI backend skeleton for campaign automation workflows.

## Stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Pydantic v2 (`pydantic-settings`)
- Docker + Docker Compose
- Structlog-based structured logging

## Project Structure

```text
campaignpilot/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── workflow/
│   ├── agents/
│   ├── evaluation/
│   └── main.py
├── alembic/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Configuration

1. Copy environment template:

```bash
cp .env.example .env
```

2. Update values as needed.

`app/core/config.py` reads settings from `.env` and environment variables.

## Run with Docker

```bash
docker compose up --build
```

API docs available at:

- http://localhost:8000/docs
- http://localhost:8000/redoc

## Local Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Notes

- Business logic, domain models, and migrations are intentionally not implemented yet.
- `alembic/` and `tests/` are prepared for future expansion.


## Creator Matching

- `POST /api/v1/campaigns/{id}/match-creators` embeds the campaign brief and returns top 5 similar creators.
- If `OPENAI_API_KEY` is not set, the API uses a deterministic mock embedding generator for local development.
- Startup initialization enables the `pgvector` extension and creates the `match_creators` similarity SQL function.
