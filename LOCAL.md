# Running Engrow API locally

## Prerequisites

- Python 3.11+ (tested on 3.14)
- The frontend repo (`engrow` / `english-work-tracker`) if you want to exercise the API through the UI — see its own `LOCAL.md`.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate.bat        # Windows CMD — use Activate.ps1 for PowerShell, source .venv/bin/activate on Linux/Mac
pip install -r requirements.txt
cp .env.example .env              # then edit FRONTEND_ORIGIN to match your frontend's actual port
alembic upgrade head
```

## Run

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload
```

- API: http://localhost:8010
- Swagger docs: http://localhost:8010/docs
- Admin panel: http://localhost:8010/admin (login with `SUPERADMIN_EMAIL` / `SUPERADMIN_PASSWORD` from `.env`)

On startup the app seeds a superadmin user, default resources, and activity tips automatically — no manual seed step needed.

## Test

```bash
pytest
```

## Common pitfalls

- **CORS errors in the browser console** almost always mean `FRONTEND_ORIGIN` in `.env` doesn't exactly match the origin the frontend is actually running on (Vite auto-shifts to the next free port if 3000 is taken — check the terminal for the real port and update `.env` to match, then restart uvicorn).
- **Adding a new SQLAlchemy model?** Register it in `app/models/__init__.py`. If you don't, `alembic revision --autogenerate` won't know the table should exist and will generate a migration that *drops* it on the next run against a database that already has it — this has bitten this project before.
- SQLite can't `ALTER COLUMN` directly. If autogenerate produces a migration with `op.alter_column(...)` on an existing SQLite table, wrap the affected operations in `with op.batch_alter_table(...) as batch_op:` (see any recent migration in `alembic/versions/` for the pattern) or it will fail with `near "ALTER": syntax error`.
