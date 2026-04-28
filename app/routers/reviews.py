from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.review import MonthlyReview
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate

router = APIRouter(prefix="/reviews", tags=["reviews"])


def _get_review_or_404(review_id: int, user: User, db: Session) -> MonthlyReview:
    review = db.query(MonthlyReview).filter(MonthlyReview.id == review_id, MonthlyReview.user_id == user.id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return review


@router.get("", response_model=list[ReviewResponse])
def list_reviews(
    plan_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(MonthlyReview)
        .filter(MonthlyReview.user_id == current_user.id, MonthlyReview.plan_id == plan_id)
        .order_by(MonthlyReview.month.desc())
        .all()
    )


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(body: ReviewCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    review = MonthlyReview(user_id=current_user.id, **body.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(review_id: int, body: ReviewUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    review = _get_review_or_404(review_id, current_user, db)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(review, field, value)
    db.commit()
    db.refresh(review)
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    review = _get_review_or_404(review_id, current_user, db)
    db.delete(review)
    db.commit()
