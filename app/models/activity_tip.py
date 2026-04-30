import json

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ActivityTip(Base):
    __tablename__ = "activity_tips"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    how: Mapped[str] = mapped_column(Text, nullable=False)
    tips_json: Mapped[str] = mapped_column(Text, default="[]")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    @property
    def tips(self) -> list[str]:
        return json.loads(self.tips_json or "[]")
