# Running Engrow API in production

## Docker (recommended)

```bash
cp .env.example .env       # fill in real secrets — see "Environment" below
python scripts/generate_vapid_keys.py   # writes vapid_private_key.pem, needed before `up`
docker compose up -d --build
```

This runs the API + a Postgres 16 container. `docker-compose.yml` overrides `DATABASE_URL` to point at the `db` service — the value in `.env` is only used for local/non-Docker runs. Migrations (`alembic upgrade head`) run automatically as part of the container's start command, every time it starts.

For a managed Postgres instance instead of the bundled `db` service, drop the `db` service from `docker-compose.yml` and set `DATABASE_URL` directly in `.env` (the compose file's `environment:` override only applies to the bundled `db` host — remove it too).

## Without Docker

There's no build step — it's a standard ASGI app. Install dependencies and run migrations against the production database:

```bash
pip install -r requirements.txt
alembic upgrade head
```

## Environment

Set real values for every variable in `.env.example`, in particular:

- `DATABASE_URL` — point at Postgres in production, not SQLite (SQLite is fine for dev/single-instance, but has no concurrent-write story and `BACKUP_DIR`/`backup_sqlite` scheduler job assumes a local file).
- `SECRET_KEY` / `ADMIN_SECRET_KEY` — real random secrets, not the defaults.
- `FRONTEND_ORIGIN` — the real deployed frontend URL (exact scheme + host, no trailing slash). CORS will silently reject every request from any other origin.
- `SUPERADMIN_EMAIL` / `SUPERADMIN_PASSWORD` — change from the placeholder before the first deploy; this account is auto-created on startup.
- `GOOGLE_CLIENT_ID` — the production OAuth Client ID (Google Cloud Console → Authorized JavaScript origins must include the production frontend URL).
- `VAPID_PRIVATE_KEY_PATH` / `VAPID_PUBLIC_KEY` — generate a **separate** production key pair with `python scripts/generate_vapid_keys.py`; don't reuse the local dev keys. Keep the private key file off git (already covered by `.gitignore`'s `*.pem` rule) and deploy it alongside the app or via your platform's secret storage.
- `SMTP_*` — needed for password-reset emails to actually send.

## Run

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8010
```

No `--reload`. Put a real ASGI server manager (systemd, Docker, your platform's process manager) in front of this rather than running it in a terminal.

## Migrations on deploy

Run `alembic upgrade head` as part of the deploy step, before the new app version starts serving traffic. Never edit a migration file that's already been applied in production — add a new one.

## Admin panel

`/admin` (sqladmin) is gated by its own login form (`SUPERADMIN_EMAIL` / `SUPERADMIN_PASSWORD`), backed by a session cookie signed with `ADMIN_SECRET_KEY` — make sure both have real, non-default values before deploying.
