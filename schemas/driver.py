from pydantic import BaseModel
from typing import Optional, List

class DriverBase(BaseModel):
    vehicle_number: Optional[str] = None
    is_active: bool = True
    status: Optional[str] = "available"  # e.g., "available", "busy", "offline"


class DriverCreate(DriverBase):
    user_id: int

class DriverRead(DriverBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class DriverUpdate(DriverBase):
    vehicle_number: Optional[str] = None
    is_active: Optional[bool] = None
