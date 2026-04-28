from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.writing import WritingEntry
from app.models.user import User
from app.schemas.writing import WritingCreate, WritingResponse, WritingUpdate

router = APIRouter(prefix="/writing", tags=["writing"])


def _get_entry_or_404(entry_id: int, user: User, db: Session) -> WritingEntry:
    entry = db.query(WritingEntry).filter(WritingEntry.id == entry_id, WritingEntry.user_id == user.id).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Writing entry not found")
    return entry


@router.get("", response_model=list[WritingResponse])
def list_entries(
    plan_id: int = Query(...),
    date: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(WritingEntry).filter(WritingEntry.user_id == current_user.id, WritingEntry.plan_id == plan_id)
    if date:
        q = q.filter(WritingEntry.date == date)
    return q.order_by(WritingEntry.created_at.asc()).all()


@router.post("", response_model=WritingResponse, status_code=status.HTTP_201_CREATED)
def create_entry(body: WritingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = WritingEntry(user_id=current_user.id, **body.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.put("/{entry_id}", response_model=WritingResponse)
def update_entry(entry_id: int, body: WritingUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = _get_entry_or_404(entry_id, current_user, db)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(entry_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = _get_entry_or_404(entry_id, current_user, db)
    db.delete(entry)
    db.commit()
