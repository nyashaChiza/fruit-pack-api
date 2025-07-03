# schemas.py
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

class ClaimStatusEnum(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class DriverClaim(BaseModel):
    id: int
    order_id: int
    driver_id: int
    status:  ClaimStatusEnum
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True


# schemas.py
class DriverClaimCreate(BaseModel):
    order_id: int


# schemas.py
class DriverClaimOut(BaseModel):
    id: int
    order_id: int
    status: str
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True

class DriverClaimList(DriverClaim):
    pass
