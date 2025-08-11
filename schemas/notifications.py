from pydantic import BaseModel
from datetime import datetime

class NotificationBase(BaseModel):
    user_id: int
    object_id: int
    message: str
    header: str
    event_type: str
    status: str
    created: datetime

class NotificationCreate(NotificationBase):
    id: int

class NotificationRead(NotificationBase):
    id: int

    class Config:
        orm_mode = True

class NotificationAlert(BaseModel):
    user_id: str
    title: str
    body: str
    timestamp: datetime
    read: bool = False