# Alembic

Alembic is configured for the SQLAlchemy models in `app/models`.

## Create migration

```bash
alembic revision --autogenerate -m "message"
```

## Apply migration

```bash
alembic upgrade head
```
