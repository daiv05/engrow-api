from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), default="You")
    avatar_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superadmin: Mapped[bool] = mapped_column(Boolean, default=False)

    plans: Mapped[list["Plan"]] = relationship("Plan", back_populates="user", cascade="all, delete-orphan")
    daily_blocks: Mapped[list["DailyBlock"]] = relationship("DailyBlock", back_populates="user", cascade="all, delete-orphan")
    writing_entries: Mapped[list["WritingEntry"]] = relationship("WritingEntry", back_populates="user", cascade="all, delete-orphan")
    resource_categories: Mapped[list["ResourceCategory"]] = relationship("ResourceCategory", back_populates="user", cascade="all, delete-orphan")
    resources: Mapped[list["Resource"]] = relationship("Resource", back_populates="user", cascade="all, delete-orphan")
    monthly_reviews: Mapped[list["MonthlyReview"]] = relationship("MonthlyReview", back_populates="user", cascade="all, delete-orphan")
