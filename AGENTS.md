# Engrow API

FastAPI backend for Engrow Tracker. RESTful API with SQLAlchemy ORM, Alembic migrations, and JWT authentication.

---

## Quick Commands

### Python Virtual Environment (Windows)

```bash
# Create virtual environment
python -m venv .venv

# Activate .venv (Windows — CMD)
.venv\Scripts\activate.bat

# Activate .venv (Windows — PowerShell)
.venv\Scripts\Activate.ps1

# Activate .venv (Linux/Mac)
source .venv/bin/activate

# Deactivate
deactivate

# Check Python version in .venv
python --version

# Check installed packages
pip list
```

### FastAPI & Dependencies

```bash
# Install dependencies from requirements.txt
pip install -r requirements.txt

# Run dev server (auto-reload on http://localhost:8010)
python main.py
# OR
uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload

# Run without reload (production-like)
uvicorn app.main:app --host 0.0.0.0 --port 8010

# Check if FastAPI is running
curl http://localhost:8010/docs
```

### Database Migrations (Alembic)

```bash
# Show current migration version
alembic current

# Create a new migration (auto-detect schema changes)
alembic revision --autogenerate -m "your message here"

# Apply all pending migrations (upgrade)
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show migration history
alembic history

# View SQL for pending migrations (dry-run)
alembic upgrade head --sql
```

### .venv Best Practices

1. **Always activate before developing:**
   ```bash
   .venv\Scripts\activate.bat
   ```
   Prompt should show `(.venv)` prefix.

2. **Never commit .venv to git** — it's in `.gitignore`.

3. **Update requirements after installing packages:**
   ```bash
   pip freeze > requirements.txt
   ```

4. **Fresh install in new machine:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate.bat
   pip install -r requirements.txt
   alembic upgrade head
   ```

5. **Reinstall all packages (if corrupted):**
   ```bash
   deactivate
   rmdir /s /q .venv
   python -m venv .venv
   .venv\Scripts\activate.bat
   pip install -r requirements.txt
   ```

---

## Architecture Overview

```
app/
├── main.py                # FastAPI app instantiation + middleware + mount routers
├── config.py              # Environment variables (Pydantic BaseSettings)
├── database.py            # SQLAlchemy engine, SessionLocal, Base
├── core/
│   ├── security.py        # JWT encode/decode, password hashing
│   ├── dependencies.py    # get_current_user, get_db (dependency injection)
│   ├── email.py           # Email sending helpers
│   ├── admin.py           # Admin utilities
│   ├── scheduler.py       # APScheduler background tasks
│   ├── rate_limit.py      # SlowAPI rate limiting
│   └── seed.py            # Database seeding
├── models/                # SQLAlchemy ORM models
│   ├── user.py
│   ├── plan.py
│   ├── block.py
│   ├── writing.py
│   ├── resource.py
│   ├── review.py
│   ├── activity_tip.py
│   └── default_resource.py
├── schemas/               # Pydantic request/response schemas
│   ├── user.py
│   ├── plan.py
│   ├── block.py
│   ├── writing.py
│   ├── resource.py
│   ├── review.py
│   ├── activity_tip.py
│   ├── auth.py
│   └── sync.py
├── routers/               # API endpoints (routes grouped by domain)
│   ├── auth.py            # Login, register, token refresh
│   ├── users.py           # Profile, preferences
│   ├── plans.py           # CRUD plans + templates
│   ├── blocks.py          # Log activities
│   ├── writing.py         # Writing entries
│   ├── resources.py       # Study links
│   ├── reviews.py         # Monthly reviews
│   ├── sync.py            # Offline-first sync endpoint
│   └── superadmin.py      # Admin-only operations
└── __init__.py

alembic/
├── env.py                 # Alembic config (migration runner)
├── script.py.mako         # Migration template
└── versions/              # Migration files (auto-generated)
    ├── e695ada82529_initial.py
    └── ...
```

**Request flow:** Client - FastAPI route - dependency injection (get_current_user, get_db) - SQLAlchemy query - Database

---

## Database

**Engine:** SQLAlchemy 2.0 + SQLite (dev) or PostgreSQL (prod).

**Base model:** All ORM models inherit from `Base` in [app/database.py](app/database.py).

**Key tables** (auto-created via Alembic):
- `user` — accounts, password hash, email
- `plan` — study plans (one per user)
- `daily_block` — activity log (30+ min/day = streak day)
- `writing_entry` — writing sessions (text, word count)
- `resource_category` — user-defined categories
- `resource` — study links
- `monthly_review` — self-evaluations
- `activity_tip` — pre-populated learning tips
- `default_resource` — seed data for new plans

### Alembic Rules

- **Never edit existing migration files** in `alembic/versions/`.
- **Always create new migrations** when schema changes:
  ```bash
  alembic revision --autogenerate -m "add column xyz"
  alembic upgrade head
  ```
- **Test migration locally** before committing.
- Timestamp migrations as `YYYYMMDDHHMMSS` (auto-generated by Alembic).

---

## Environment Variables

File: `.env` (in project root, not in git).

```env
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-super-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ADMIN_EMAIL=admin@example.com
```

Load via `config.py`:
```python
from app.config import settings
print(settings.SECRET_KEY)
```

---

## Authentication

**Scheme:** JWT (JSON Web Token) + Bearer header.

**Flow:**
1. Client calls `POST /auth/login` with username/password.
2. Server validates, generates access + refresh tokens (JWT).
3. Client stores tokens (localStorage for PWA).
4. Client sends `Authorization: Bearer <access_token>` with every request.
5. Server verifies via `get_current_user()` dependency.

**Token structure:**
- `access_token` — short-lived (30 min default).
- `refresh_token` — long-lived (7 days default).

See [app/core/security.py](app/core/security.py) and [app/core/dependencies.py](app/core/dependencies.py).

---

## API Endpoints Structure

Routes are organized by domain in `app/routers/`:

```
POST   /auth/register           — Create account
POST   /auth/login              — Get tokens
POST   /auth/refresh            — Refresh access token
POST   /auth/logout             — Invalidate tokens (optional)

GET    /users/me                — Current user profile
PUT    /users/me                — Update profile
GET    /users/{user_id}         — Get user (admin only)

POST   /plans                   — Create plan
GET    /plans                   — List user's plans
GET    /plans/{plan_id}         — Get plan details
PUT    /plans/{plan_id}         — Update plan
DELETE /plans/{plan_id}         — Delete plan
POST   /plans/templates         — Get weekly templates

POST   /blocks                  — Log activity
GET    /blocks                  — List blocks (filtered by plan_id, date)
PUT    /blocks/{block_id}       — Update block
DELETE /blocks/{block_id}       — Delete block

POST   /writing                 — Save writing entry
GET    /writing                 — List entries (filtered by date)
PUT    /writing/{entry_id}      — Update entry
DELETE /writing/{entry_id}      — Delete entry

POST   /resources               — Create resource
GET    /resources               — List resources (filtered by category)
PUT    /resources/{resource_id} — Update resource
DELETE /resources/{resource_id} — Delete resource

POST   /reviews                 — Save monthly review
GET    /reviews                 — List reviews (filtered by month)
PUT    /reviews/{review_id}     — Update review

GET    /sync                    — Offline-first sync (get all user data)
POST   /sync                    — Sync local changes (bulk upsert)

GET    /superadmin/...          — Admin endpoints (requires is_superadmin=True)
```

**Response format:**
```json
{
  "data": {...},
  "message": "Success",
  "status_code": 200
}
```

---

## Pydantic Models (Schemas)

All request/response bodies validated via Pydantic in `app/schemas/`.

**Rules:**
- Use `BaseModel` for simple payloads.
- Use `Field(description="...")` for OpenAPI docs.
- Use custom validators (`@field_validator`) for business logic.
- Separate read schemas (with `id`, `created_at`) from write schemas.

Example:
```python
from pydantic import BaseModel, Field

class PlanCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    daily_goal_minutes: int = Field(default=30, ge=10)

class PlanRead(PlanCreate):
    id: int
    user_id: int
    created_at: datetime
```

---

## Common Tasks

**Add a new API endpoint**
1. Create ORM model in [app/models/](app/models/) if needed.
2. Create Pydantic schemas in [app/schemas/](app/schemas/).
3. Create router file or add to existing in [app/routers/](app/routers/).
4. Mount router in [app/main.py](app/main.py): `app.include_router(your_router, prefix="/prefix")`.
5. Test via `/docs` (Swagger UI) or curl.

**Add a database column**
1. Add field to ORM model in [app/models/](app/models/).
2. Create migration:
   ```bash
   alembic revision --autogenerate -m "add column to user"
   ```
3. Review generated migration in `alembic/versions/`.
4. Apply:
   ```bash
   alembic upgrade head
   ```

**Update dependencies**
1. Install new package:
   ```bash
   pip install package-name
   ```
2. Freeze to requirements:
   ```bash
   pip freeze > requirements.txt
   ```
3. Commit both files.

**Debug database queries**
1. Enable SQLAlchemy echo in [app/database.py](app/database.py):
   ```python
   engine = create_engine(
       DATABASE_URL,
       echo=True  # Print all SQL queries
   )
   ```
2. Watch terminal output while making requests.

---

## Type Hints (Python Best Practice)

Always use type hints. FastAPI leverages them for validation and docs.

```python
from typing import Optional, List
from datetime import datetime

# Good
def get_user(user_id: int) -> Optional[UserRead]:
    ...

def list_plans(plan_ids: List[int]) -> List[PlanRead]:
    ...

# Avoid
def get_user(user_id):  # No type hint
    ...
```

---

## Testing (Optional, Best Practice)

Use `pytest` for unit and integration tests.

```bash
pip install pytest pytest-asyncio httpx
pytest
```

Test structure (not implemented yet, but recommended):
```
tests/
├── test_auth.py
├── test_users.py
├── test_plans.py
└── conftest.py  # Shared fixtures (test DB, client)
```

---

## Error Handling

Use FastAPI's `HTTPException` for user-facing errors:

```python
from fastapi import HTTPException, status

if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )
```

**Common status codes:**
- `200 OK` — Success
- `201 Created` — Resource created
- `204 No Content` — Success with no body
- `400 Bad Request` — Validation error
- `401 Unauthorized` — Missing/invalid token
- `403 Forbidden` — Token valid but no permission
- `404 Not Found` — Resource not found
- `500 Internal Server Error` — Server error

---

