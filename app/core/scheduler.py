import glob
import os
import shutil
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings

_scheduler = BackgroundScheduler()


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
    _scheduler.start()


def stop_scheduler() -> None:
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
