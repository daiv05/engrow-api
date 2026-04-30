import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, get_superadmin
from app.models.activity_tip import ActivityTip
from app.models.block import DailyBlock
from app.models.default_resource import DefaultResource
from app.models.user import User
from app.schemas.activity_tip import ActivityTipCreate, ActivityTipResponse, ActivityTipUpdate
from app.schemas.default_resource import (
    DefaultResourceCreate,
    DefaultResourceResponse,
    DefaultResourceUpdate,
)

router = APIRouter(prefix="/superadmin", tags=["superadmin"])


class AdminUserRow(BaseModel):
    id: int
    email: str
    display_name: str
    created_at: datetime
    is_active: bool
    total_minutes: int


@router.get("/users", response_model=list[AdminUserRow])
def list_users(db: Session = Depends(get_db), _: User = Depends(get_superadmin)):
    subq = (
        db.query(DailyBlock.user_id, func.sum(DailyBlock.duration_minutes).label("total_minutes"))
        .group_by(DailyBlock.user_id)
        .subquery()
    )
    rows = (
        db.query(User, func.coalesce(subq.c.total_minutes, 0).label("total_minutes"))
        .outerjoin(subq, User.id == subq.c.user_id)
        .order_by(User.id)
        .all()
    )
    return [
        AdminUserRow(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            created_at=user.created_at,
            is_active=user.is_active,
            total_minutes=int(total_minutes),
        )
        for user, total_minutes in rows
    ]


@router.get("/default-resources", response_model=list[DefaultResourceResponse])
def list_default_resources(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return (
        db.query(DefaultResource)
        .order_by(DefaultResource.category_name, DefaultResource.sort_order)
        .all()
    )


@router.post("/default-resources", response_model=DefaultResourceResponse, status_code=201)
def create_default_resource(
    body: DefaultResourceCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_superadmin),
):
    resource = DefaultResource(
        category_name=body.category_name,
        title=body.title,
        url=body.url,
        tags_json=json.dumps(body.tags),
        sort_order=body.sort_order,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.put("/default-resources/{resource_id}", response_model=DefaultResourceResponse)
def update_default_resource(
    resource_id: int,
    body: DefaultResourceUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_superadmin),
):
    resource = db.get(DefaultResource, resource_id)
    if resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    if body.category_name is not None:
        resource.category_name = body.category_name
    if body.title is not None:
        resource.title = body.title
    if body.url is not None:
        resource.url = body.url
    if body.tags is not None:
        resource.tags_json = json.dumps(body.tags)
    if body.sort_order is not None:
        resource.sort_order = body.sort_order
    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/default-resources/{resource_id}", status_code=204)
def delete_default_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_superadmin),
):
    resource = db.get(DefaultResource, resource_id)
    if resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    db.delete(resource)
    db.commit()


# ---------------------------------------------------------------------------
# Activity tips
# ---------------------------------------------------------------------------


@router.get("/activity-tips", response_model=list[ActivityTipResponse])
def list_activity_tips(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return (
        db.query(ActivityTip)
        .order_by(ActivityTip.sort_order, ActivityTip.activity_type)
        .all()
    )


@router.post("/activity-tips", response_model=ActivityTipResponse, status_code=201)
def create_activity_tip(
    body: ActivityTipCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_superadmin),
):
    tip = ActivityTip(
        activity_type=body.activity_type,
        how=body.how,
        tips_json=json.dumps(body.tips),
        sort_order=body.sort_order,
    )
    db.add(tip)
    db.commit()
    db.refresh(tip)
    return tip


@router.put("/activity-tips/{tip_id}", response_model=ActivityTipResponse)
def update_activity_tip(
    tip_id: int,
    body: ActivityTipUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_superadmin),
):
    tip = db.get(ActivityTip, tip_id)
    if tip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity tip not found")
    if body.activity_type is not None:
        tip.activity_type = body.activity_type
    if body.how is not None:
        tip.how = body.how
    if body.tips is not None:
        tip.tips_json = json.dumps(body.tips)
    if body.sort_order is not None:
        tip.sort_order = body.sort_order
    db.commit()
    db.refresh(tip)
    return tip


@router.delete("/activity-tips/{tip_id}", status_code=204)
def delete_activity_tip(
    tip_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_superadmin),
):
    tip = db.get(ActivityTip, tip_id)
    if tip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity tip not found")
    db.delete(tip)
    db.commit()
