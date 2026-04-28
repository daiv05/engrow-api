from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.block import DailyBlock
from app.models.user import User
from app.schemas.block import BlockCreate, BlockResponse, BlockTotalsResponse, BlockUpdate

router = APIRouter(prefix="/blocks", tags=["blocks"])


def _get_block_or_404(block_id: int, user: User, db: Session) -> DailyBlock:
    block = db.query(DailyBlock).filter(DailyBlock.id == block_id, DailyBlock.user_id == user.id).first()
    if not block:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")
    return block


@router.get("", response_model=list[BlockResponse])
def list_blocks(
    plan_id: int = Query(...),
    date: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(DailyBlock).filter(DailyBlock.user_id == current_user.id, DailyBlock.plan_id == plan_id)
    if date:
        q = q.filter(DailyBlock.date == date)
    return q.order_by(DailyBlock.created_at.asc()).all()


@router.get("/totals", response_model=list[BlockTotalsResponse])
def get_totals(
    plan_id: int = Query(...),
    dates: list[str] = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(DailyBlock.date, func.sum(DailyBlock.duration_minutes).label("total_minutes"))
        .filter(DailyBlock.user_id == current_user.id, DailyBlock.plan_id == plan_id, DailyBlock.date.in_(dates))
        .group_by(DailyBlock.date)
        .all()
    )
    return [BlockTotalsResponse(date=row.date, total_minutes=row.total_minutes) for row in rows]


@router.post("", response_model=BlockResponse, status_code=status.HTTP_201_CREATED)
def create_block(body: BlockCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    block = DailyBlock(user_id=current_user.id, **body.model_dump())
    db.add(block)
    db.commit()
    db.refresh(block)
    return block


@router.put("/{block_id}", response_model=BlockResponse)
def update_block(block_id: int, body: BlockUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    block = _get_block_or_404(block_id, current_user, db)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(block, field, value)
    db.commit()
    db.refresh(block)
    return block


@router.delete("/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_block(block_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    block = _get_block_or_404(block_id, current_user, db)
    db.delete(block)
    db.commit()
