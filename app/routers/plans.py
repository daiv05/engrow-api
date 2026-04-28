from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.plan import Plan
from app.models.user import User
from app.schemas.plan import PlanCreate, PlanResponse, PlanUpdate

router = APIRouter(prefix="/plans", tags=["plans"])


def _get_plan_or_404(plan_id: int, user: User, db: Session) -> Plan:
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.user_id == user.id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan


@router.get("", response_model=list[PlanResponse])
def list_plans(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Plan).filter(Plan.user_id == current_user.id).order_by(Plan.created_at.desc()).all()


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(body: PlanCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = Plan(user_id=current_user.id, **body.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _get_plan_or_404(plan_id, current_user, db)


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(plan_id: int, body: PlanUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = _get_plan_or_404(plan_id, current_user, db)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(plan, field, value)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = _get_plan_or_404(plan_id, current_user, db)
    db.delete(plan)
    db.commit()


@router.post("/{plan_id}/activate", response_model=PlanResponse)
def activate_plan(plan_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = _get_plan_or_404(plan_id, current_user, db)
    db.query(Plan).filter(Plan.user_id == current_user.id).update({"is_active": False})
    plan.is_active = True
    db.commit()
    db.refresh(plan)
    return plan
