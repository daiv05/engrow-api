import json
from pydantic import BaseModel, field_validator, model_serializer


class CategoryCreate(BaseModel):
    plan_id: int
    name: str
    created_at: int


class CategoryResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    name: str
    created_at: int

    model_config = {"from_attributes": True}


class ResourceCreate(BaseModel):
    plan_id: int
    category_id: int
    title: str
    url: str | None = None
    notes: str | None = None
    tags: list[str] = []
    created_at: int


class ResourceUpdate(BaseModel):
    title: str | None = None
    url: str | None = None
    notes: str | None = None
    tags: list[str] | None = None
    category_id: int | None = None


class ResourceResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    category_id: int
    title: str
    url: str | None
    notes: str | None
    tags: list[str]
    created_at: int

    model_config = {"from_attributes": True}

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
