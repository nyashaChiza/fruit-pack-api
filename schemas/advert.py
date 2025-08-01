from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AdvertBase(BaseModel):
    title: str
    description: str
    status: str = "active"  
    created: datetime = datetime.now()
    updated: Optional[datetime] = None

class AdvertCreate(AdvertBase):
    pass

class AdvertRead(AdvertBase):
    id: int

class AdvertUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

    class Config:
        orm_mode = True
