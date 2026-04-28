import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.resource import Resource, ResourceCategory
from app.models.user import User
from app.schemas.resource import (
    CategoryCreate,
    CategoryResponse,
    ResourceCreate,
    ResourceResponse,
    ResourceUpdate,
)

router = APIRouter(tags=["resources"])


# ── Categories ──────────────────────────────────────────────────────────────

@router.get("/resource-categories", response_model=list[CategoryResponse])
def list_categories(
    plan_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(ResourceCategory)
        .filter(ResourceCategory.user_id == current_user.id, ResourceCategory.plan_id == plan_id)
        .order_by(ResourceCategory.created_at.asc())
        .all()
    )


@router.post("/resource-categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(body: CategoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cat = ResourceCategory(user_id=current_user.id, **body.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/resource-categories/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(cat_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cat = db.query(ResourceCategory).filter(ResourceCategory.id == cat_id, ResourceCategory.user_id == current_user.id).first()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    db.delete(cat)
    db.commit()


# ── Resources ────────────────────────────────────────────────────────────────

@router.get("/resources", response_model=list[ResourceResponse])
def list_resources(
    plan_id: int = Query(...),
    category_id: int | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Resource).filter(Resource.user_id == current_user.id, Resource.plan_id == plan_id)
    if category_id is not None:
        q = q.filter(Resource.category_id == category_id)
    return q.order_by(Resource.created_at.asc()).all()


@router.post("/resources", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
def create_resource(body: ResourceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = body.model_dump()
    tags = data.pop("tags", [])
    resource = Resource(user_id=current_user.id, tags_json=json.dumps(tags), **data)
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.put("/resources/{resource_id}", response_model=ResourceResponse)
def update_resource(resource_id: int, body: ResourceUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id, Resource.user_id == current_user.id).first()
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    data = body.model_dump(exclude_none=True)
    if "tags" in data:
        resource.tags_json = json.dumps(data.pop("tags"))
    for field, value in data.items():
        setattr(resource, field, value)
    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(resource_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id, Resource.user_id == current_user.id).first()
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    db.delete(resource)
    db.commit()
