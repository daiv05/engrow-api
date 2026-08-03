# Engrow API

FastAPI backend for [Engrow](https://github.com/daiv05/english-work-tracker) — an English study bitácora/tracker. SQLAlchemy 2 + Alembic + JWT auth, with Google Sign-In and Web Push.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8010
```

See [LOCAL.md](LOCAL.md) for the full local setup (including common pitfalls) and [PROD.md](PROD.md) for deployment.

## Tech stack

FastAPI · SQLAlchemy 2 · Alembic · Pydantic Settings · APScheduler · pywebpush · sqladmin

## Docs

- [LOCAL.md](LOCAL.md) — run it locally
- [PROD.md](PROD.md) — deploy it
- [CLAUDE.md](CLAUDE.md) — architecture, conventions, and rules for anyone (human or AI) making changes here
