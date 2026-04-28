from pydantic import BaseModel


class BlockCreate(BaseModel):
    plan_id: int
    date: str
    start_time: str | None = None
    type: str
    resource_id: int | None = None
    custom_resource_text: str | None = None
    duration_minutes: int
    notes: str | None = None
    created_at: int


class BlockUpdate(BaseModel):
    start_time: str | None = None
    type: str | None = None
    resource_id: int | None = None
    custom_resource_text: str | None = None
    duration_minutes: int | None = None
    notes: str | None = None


class BlockResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    date: str
    start_time: str | None
    type: str
    resource_id: int | None
    custom_resource_text: str | None
    duration_minutes: int
    notes: str | None
    created_at: int

    model_config = {"from_attributes": True}


class BlockTotalsResponse(BaseModel):
    date: str
    total_minutes: int
