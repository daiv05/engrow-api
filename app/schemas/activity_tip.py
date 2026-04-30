from pydantic import BaseModel


class ActivityTipCreate(BaseModel):
    activity_type: str
    how: str
    tips: list[str] = []
    sort_order: int = 0


class ActivityTipUpdate(BaseModel):
    activity_type: str | None = None
    how: str | None = None
    tips: list[str] | None = None
    sort_order: int | None = None


class ActivityTipResponse(BaseModel):
    id: int
    activity_type: str
    how: str
    tips: list[str]
    sort_order: int

    model_config = {"from_attributes": True}
