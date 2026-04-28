from pydantic import BaseModel


class ReviewCreate(BaseModel):
    plan_id: int
    month: str  # YYYY-MM
    answers_json: str = "{}"
    notes: str | None = None
    created_at: int


class ReviewUpdate(BaseModel):
    answers_json: str | None = None
    notes: str | None = None


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    month: str
    answers_json: str
    notes: str | None
    created_at: int

    model_config = {"from_attributes": True}
