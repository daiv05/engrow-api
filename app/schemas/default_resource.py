from pydantic import BaseModel


class DefaultResourceCreate(BaseModel):
    category_name: str
    title: str
    url: str | None = None
    tags: list[str] = []
    sort_order: int = 0


class DefaultResourceUpdate(BaseModel):
    category_name: str | None = None
    title: str | None = None
    url: str | None = None
    tags: list[str] | None = None
    sort_order: int | None = None


class DefaultResourceResponse(BaseModel):
    id: int
    category_name: str
    title: str
    url: str | None
    tags: list[str]
    sort_order: int

    model_config = {"from_attributes": True}
