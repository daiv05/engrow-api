from pydantic import BaseModel


class WritingCreate(BaseModel):
    plan_id: int
    date: str
    text: str = ""
    word_count: int = 0
    active_time_minutes: int = 0
    linked_block_id: int | None = None
    prompt: str | None = None
    created_at: int


class WritingUpdate(BaseModel):
    text: str | None = None
    word_count: int | None = None
    active_time_minutes: int | None = None
    linked_block_id: int | None = None
    prompt: str | None = None


class WritingResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    date: str
    text: str
    word_count: int
    active_time_minutes: int
    linked_block_id: int | None
    prompt: str | None
    created_at: int

    model_config = {"from_attributes": True}
