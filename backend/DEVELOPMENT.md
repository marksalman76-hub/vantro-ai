# Backend Development Guide

## Prerequisites

- Python 3.11+
- PostgreSQL 15+ (production) or SQLite (tests)

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Environment variables

Copy `.env.example` to `.env` and fill in values:

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/vantro_dev
SECRET_KEY=your-secret-key
```

## Running locally

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at `http://localhost:8000/docs`.

## Running tests

Tests use SQLite in-memory — no database setup required:

```bash
# From project root
python -m pytest backend/tests/test_auth.py -v

# With coverage
python -m pytest backend/tests/ -v --cov=app --cov-report=term-missing
```

## Database migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

## Project structure

```
backend/
├── app/
│   ├── auth/          # JWT + password hashing
│   ├── models/        # SQLAlchemy models
│   ├── routes/        # FastAPI routers
│   ├── database.py    # Engine + session factory
│   └── main.py        # App entrypoint
├── alembic/           # Migrations
└── tests/             # pytest test suite
```

## Key conventions

- All API routes are prefixed with `/api/`
- Auth routes live under `/api/auth/`
- Database sessions are injected via `Depends(get_db)`
- Tests override `get_db` with a SQLite in-memory session using `StaticPool`
