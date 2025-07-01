from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class OrderItemBase(BaseModel):
    product_id: int
    name: str  # Product name at time of order
    quantity: int
    price: float  # Capture price at time of order

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    status: Optional[str] = "pending"

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[str] = None

class OrderResponse(OrderBase):
    id: int
    user_id: int
    created: datetime
    updated: datetime
    items: Optional[List[OrderItemResponse]] = []
    total: float

    class Config:
        from_attributes = True

