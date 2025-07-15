from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import notifications
from db.models.notifications import Notification
from db.session import get_db

router = APIRouter(tags=["notifications"])

@router.post("/", response_model=notifications.NotificationRead)
def create_notification(notification: notifications.NotificationCreate, db: Session = Depends(get_db)):
    db_notification = Notification(**notification.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

@router.get("/user/{user_id}/unseen", response_model=list[notifications.NotificationRead])
def get_user_unseen_notifications(user_id: int, db: Session = Depends(get_db)):
    return db.query(Notification).filter_by(user_id=user_id, status="unseen").all()

@router.get("/unseen", response_model=list[notifications.NotificationRead])
def get_all_unseen_notifications(db: Session = Depends(get_db)):
    return db.query(Notification).filter_by(status="unseen").all()

@router.put("/{notification_id}/mark-seen", response_model=notifications.NotificationRead)
def mark_notification_seen(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(Notification).filter_by(id=notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.status = "seen"
    db.commit()
    db.refresh(notification)
    return notification
