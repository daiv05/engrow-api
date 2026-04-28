from sqlalchemy import String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    level_from: Mapped[str] = mapped_column(String(10), default="A2")
    level_to: Mapped[str] = mapped_column(String(10), default="B2")
    daily_goal_minutes: Mapped[int] = mapped_column(Integer, default=90)
    template_json: Mapped[str] = mapped_column(Text, default="{}")
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="plans")
    daily_blocks: Mapped[list["DailyBlock"]] = relationship("DailyBlock", back_populates="plan", cascade="all, delete-orphan")
    writing_entries: Mapped[list["WritingEntry"]] = relationship("WritingEntry", back_populates="plan", cascade="all, delete-orphan")
    resource_categories: Mapped[list["ResourceCategory"]] = relationship("ResourceCategory", back_populates="plan", cascade="all, delete-orphan")
    resources: Mapped[list["Resource"]] = relationship("Resource", back_populates="plan", cascade="all, delete-orphan")
    monthly_reviews: Mapped[list["MonthlyReview"]] = relationship("MonthlyReview", back_populates="plan", cascade="all, delete-orphan")
