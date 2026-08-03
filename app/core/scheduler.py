import glob
import os
import shutil
from datetime import date, datetime

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.block import DailyBlock
from app.models.plan import Plan
from app.models.push_subscription import PushSubscription
from app.routers.push import _send

_scheduler = BackgroundScheduler()


def send_streak_risk_pushes() -> None:
    db: Session = SessionLocal()
    try:
        today = date.today().isoformat()
        plans = db.query(Plan).filter(Plan.is_active.is_(True)).all()
        for plan in plans:
            total_minutes = (
                db.query(DailyBlock)
                .filter(DailyBlock.plan_id == plan.id, DailyBlock.date == today)
                .with_entities(DailyBlock.duration_minutes)
                .all()
            )
            minutes_logged = sum(m[0] for m in total_minutes)
            if minutes_logged >= plan.daily_goal_minutes:
                continue
            subscriptions = (
                db.query(PushSubscription).filter(PushSubscription.user_id == plan.user_id).all()
            )
            remaining = plan.daily_goal_minutes - minutes_logged
            for subscription in subscriptions:
                _send(
                    subscription,
                    "Tu racha está en riesgo",
                    f"Te faltan {remaining} min hoy para no perderla.",
                    db,
                )
    finally:
        db.close()


def backup_sqlite() -> None:
    src = settings.database_url.replace("sqlite:///./", "").replace("sqlite:///", "")
    if not os.path.exists(src):
        return

    os.makedirs(settings.backup_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = os.path.join(settings.backup_dir, f"engrow_{ts}.db")
    shutil.copy2(src, dst)

    # Keep only the last 10 backups
    files = sorted(glob.glob(os.path.join(settings.backup_dir, "engrow_*.db")))
    for old in files[:-10]:
        os.remove(old)


def start_scheduler() -> None:
    _scheduler.add_job(
        backup_sqlite,
        "interval",
        hours=settings.backup_interval_hours,
        id="sqlite_backup",
        replace_existing=True,
    )
    _scheduler.add_job(
        send_streak_risk_pushes,
        "cron",
        hour=20,
        minute=0,
        id="streak_risk_push",
        replace_existing=True,
    )
    _scheduler.start()


def stop_scheduler() -> None:
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
