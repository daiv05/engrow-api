from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import hash_password
from app.models.user import User


def seed_superadmin(db: Session) -> None:
    existing = db.query(User).filter_by(email=settings.superadmin_email).first()
    if existing:
        if not existing.is_superadmin:
            existing.is_superadmin = True
            db.commit()
        return

    superadmin = User(
        email=settings.superadmin_email,
        password_hash=hash_password(settings.superadmin_password),
        display_name="Superadmin",
        is_active=True,
        is_superadmin=True,
    )
    db.add(superadmin)
    db.commit()
