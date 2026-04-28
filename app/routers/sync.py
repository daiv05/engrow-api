import json
import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.block import DailyBlock
from app.models.plan import Plan
from app.models.resource import Resource, ResourceCategory
from app.models.review import MonthlyReview
from app.models.user import User
from app.models.writing import WritingEntry
from app.schemas.sync import SyncImportRequest, SyncImportResponse

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/import", response_model=SyncImportResponse, status_code=status.HTTP_201_CREATED)
def import_local_data(
    body: SyncImportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_plans = db.query(Plan).filter(Plan.user_id == current_user.id).count()
    if existing_plans > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already has data. Import is only allowed once on a fresh account.",
        )

    now_ms = int(time.time() * 1000)

    # Map local_id → server id for plans and categories
    plan_id_map: dict[int, int] = {}
    cat_id_map: dict[int, int] = {}

    # Plans
    for p in body.plans:
        plan = Plan(
            user_id=current_user.id,
            name=p.name,
            description=p.description,
            level_from=p.level_from,
            level_to=p.level_to,
            daily_goal_minutes=p.daily_goal_minutes,
            template_json=p.template_json,
            is_active=p.is_active,
            created_at=p.created_at or now_ms,
            updated_at=p.updated_at or now_ms,
        )
        db.add(plan)
        db.flush()
        if p.local_id is not None:
            plan_id_map[p.local_id] = plan.id

    # Resource categories
    for c in body.resource_categories:
        server_plan_id = plan_id_map.get(c.plan_local_id)
        if server_plan_id is None:
            continue
        cat = ResourceCategory(
            user_id=current_user.id,
            plan_id=server_plan_id,
            name=c.name,
            created_at=c.created_at or now_ms,
        )
        db.add(cat)
        db.flush()
        if c.local_id is not None:
            cat_id_map[c.local_id] = cat.id

    # Resources
    for r in body.resources:
        server_plan_id = plan_id_map.get(r.plan_local_id)
        server_cat_id = cat_id_map.get(r.category_local_id)
        if server_plan_id is None or server_cat_id is None:
            continue
        db.add(Resource(
            user_id=current_user.id,
            plan_id=server_plan_id,
            category_id=server_cat_id,
            title=r.title,
            url=r.url,
            notes=r.notes,
            tags_json=json.dumps(r.tags),
            created_at=r.created_at or now_ms,
        ))

    # Daily blocks
    for b in body.daily_blocks:
        server_plan_id = plan_id_map.get(b.plan_local_id)
        if server_plan_id is None:
            continue
        db.add(DailyBlock(
            user_id=current_user.id,
            plan_id=server_plan_id,
            date=b.date,
            start_time=b.start_time,
            type=b.type,
            resource_id=b.resource_id,
            custom_resource_text=b.custom_resource_text,
            duration_minutes=b.duration_minutes,
            notes=b.notes,
            created_at=b.created_at or now_ms,
        ))

    # Writing entries
    for w in body.writing_entries:
        server_plan_id = plan_id_map.get(w.plan_local_id)
        if server_plan_id is None:
            continue
        db.add(WritingEntry(
            user_id=current_user.id,
            plan_id=server_plan_id,
            date=w.date,
            text=w.text,
            word_count=w.word_count,
            active_time_minutes=w.active_time_minutes,
            prompt=w.prompt,
            created_at=w.created_at or now_ms,
        ))

    # Monthly reviews
    for rev in body.monthly_reviews:
        server_plan_id = plan_id_map.get(rev.plan_local_id)
        if server_plan_id is None:
            continue
        db.add(MonthlyReview(
            user_id=current_user.id,
            plan_id=server_plan_id,
            month=rev.month,
            answers_json=rev.answers_json,
            notes=rev.notes,
            created_at=rev.created_at or now_ms,
        ))

    db.commit()

    return SyncImportResponse(
        imported={
            "plans": len(body.plans),
            "resource_categories": len(body.resource_categories),
            "resources": len(body.resources),
            "daily_blocks": len(body.daily_blocks),
            "writing_entries": len(body.writing_entries),
            "monthly_reviews": len(body.monthly_reviews),
        }
    )
