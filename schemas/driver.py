from pydantic import BaseModel
from typing import Optional, List

class DriverBase(BaseModel):
    id: Optional[int] = None
    vehicle_number: Optional[str] = None
    is_active: bool = True
    status: Optional[str] = "available"  # e.g., "available", "busy", "offline"


class DriverCreate(BaseModel):
    user_id: int
    vehicle_number: Optional[str] = None
    is_active: bool = True
    status: Optional[str] = "available"  # e.g., "available", "busy", "offline"

class DriverRead(DriverBase):
    user_id: int
    driver_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        orm_mode = True

class DriverUpdate(BaseModel):
    vehicle_number: Optional[str] = None
    status: Optional[str] = "available"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class DriverLocationUpdate(BaseModel):
    latitude: float
    longitude: float