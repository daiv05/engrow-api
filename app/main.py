from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.config import settings
from app.core.admin import create_admin
from app.core.rate_limit import limiter
from app.core.scheduler import start_scheduler, stop_scheduler
from app.core.seed import seed_superadmin
from app.database import engine, SessionLocal
from app.routers import auth, blocks, plans, resources, reviews, sync, users, writing


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        seed_superadmin(db)
    finally:
        db.close()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Engrow API",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Admin panel at /admin
create_admin(app, engine)

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(plans.router)
app.include_router(blocks.router)
app.include_router(writing.router)  # noqa: F401
app.include_router(resources.router)
app.include_router(reviews.router)
app.include_router(sync.router)


@app.get("/health")
def health():
    return {"status": "ok"}
