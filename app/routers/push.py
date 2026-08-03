import json

from fastapi import APIRouter, Depends, status
from pywebpush import WebPushException, webpush
from sqlalchemy.orm import Session

from app.config import settings
from app.core.dependencies import get_current_user, get_db
from app.models.push_subscription import PushSubscription
from app.models.user import User
from app.schemas.push import PushSubscriptionCreate, PushUnsubscribeRequest

router = APIRouter(prefix="/push", tags=["push"])


def _send(subscription: PushSubscription, title: str, body: str, db: Session) -> None:
    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
            },
            data=json.dumps({"title": title, "body": body}),
            vapid_private_key=settings.vapid_private_key_path,
            vapid_claims={"sub": f"mailto:{settings.vapid_admin_email}"},
        )
    except WebPushException as exc:
        if exc.response is not None and exc.response.status_code in (404, 410):
            db.delete(subscription)
            db.commit()


@router.post("/subscribe", status_code=status.HTTP_204_NO_CONTENT)
def subscribe(
    body: PushSubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(PushSubscription).filter(PushSubscription.endpoint == body.endpoint).first()
    if existing:
        existing.user_id = current_user.id
        existing.p256dh = body.keys.p256dh
        existing.auth = body.keys.auth
    else:
        db.add(
            PushSubscription(
                user_id=current_user.id,
                endpoint=body.endpoint,
                p256dh=body.keys.p256dh,
                auth=body.keys.auth,
            )
        )
    db.commit()


@router.delete("/subscribe", status_code=status.HTTP_204_NO_CONTENT)
def unsubscribe(
    body: PushUnsubscribeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(PushSubscription).filter(
        PushSubscription.endpoint == body.endpoint,
        PushSubscription.user_id == current_user.id,
    ).delete()
    db.commit()


@router.post("/test", status_code=status.HTTP_204_NO_CONTENT)
def send_test_push(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subscriptions = db.query(PushSubscription).filter(PushSubscription.user_id == current_user.id).all()
    for subscription in subscriptions:
        _send(subscription, "Engrow", "Notificaciones push activadas.", db)
