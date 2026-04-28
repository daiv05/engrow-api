from pydantic import BaseModel


class SyncPlan(BaseModel):
    name: str
    description: str | None = None
    level_from: str = "A2"
    level_to: str = "B2"
    daily_goal_minutes: int = 90
    template_json: str = "{}"
    is_active: bool = False
    created_at: int
    updated_at: int
    local_id: int | None = None


class SyncBlock(BaseModel):
    plan_local_id: int
    date: str
    start_time: str | None = None
    type: str
    resource_id: int | None = None
    custom_resource_text: str | None = None
    duration_minutes: int
    notes: str | None = None
    created_at: int


class SyncWriting(BaseModel):
    plan_local_id: int
    date: str
    text: str = ""
    word_count: int = 0
    active_time_minutes: int = 0
    prompt: str | None = None
    created_at: int


class SyncCategory(BaseModel):
    plan_local_id: int
    name: str
    created_at: int
    local_id: int | None = None


class SyncResource(BaseModel):
    plan_local_id: int
    category_local_id: int
    title: str
    url: str | None = None
    notes: str | None = None
    tags: list[str] = []
    created_at: int


class SyncReview(BaseModel):
    plan_local_id: int
    month: str
    answers_json: str = "{}"
    notes: str | None = None
    created_at: int


class SyncImportRequest(BaseModel):
    plans: list[SyncPlan] = []
    daily_blocks: list[SyncBlock] = []
    writing_entries: list[SyncWriting] = []
    resource_categories: list[SyncCategory] = []
    resources: list[SyncResource] = []
    monthly_reviews: list[SyncReview] = []


class SyncImportResponse(BaseModel):
    imported: dict[str, int]
