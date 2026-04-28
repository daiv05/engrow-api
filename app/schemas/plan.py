from pydantic import BaseModel


class PlanCreate(BaseModel):
    name: str
    description: str | None = None
    level_from: str = "A2"
    level_to: str = "B2"
    daily_goal_minutes: int = 90
    template_json: str = "{}"
    created_at: int
    updated_at: int


class PlanUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    level_from: str | None = None
    level_to: str | None = None
    daily_goal_minutes: int | None = None
    template_json: str | None = None
    updated_at: int | None = None


class PlanResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: str | None
    level_from: str
    level_to: str
    daily_goal_minutes: int
    template_json: str
    is_active: bool
    created_at: int
    updated_at: int

    model_config = {"from_attributes": True}
