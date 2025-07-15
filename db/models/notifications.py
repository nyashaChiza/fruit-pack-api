from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base
from sqlalchemy.orm import Session


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    header = Column(String,nullable=False)
    event_type = Column(String, nullable=False)
    object_id = Column(Integer, nullable=False)
    status = Column(String, default="unseen")  # unseen, seen, etc.
    created = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


def notify_user(
    db: Session,
    user_id: int,
    message: str,
    header: str,
    event_type: str,
    object_id: int
):
    notif = Notification(
        user_id=user_id,
        message=message,
        header=header,
        event_type=event_type,
        object_id=object_id,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif
