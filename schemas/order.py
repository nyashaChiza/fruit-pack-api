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
        from_attributes = True

class OrderBase(BaseModel):
    driver_id: Optional[int] = None  # Optional driver ID for delivery
    customer_name: Optional[str] = None  # Customer's name for delivery
    order_number: Optional[str] = None  # Unique order number
    customer_phone: Optional[str] = None  # Customer's phone number for delivery
    destination_address: Optional[str] = None  # Delivery address
    delivery_status: Optional[str]
    payment_status: Optional[str]
    delivery_code: Optional[int]
    payment_method: Optional[str] = None  # e.g., 'card', 'cash', 'paypal'
    destination_latitude: Optional[float]
    destination_longitude: Optional[float]
    distance_from_driver: Optional[float] = None  # 👈 added

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    delivery_code: Optional[int]

class OrderResponse(OrderBase):
    id: int
    user_id: int
    created: datetime
    updated: datetime
    items: Optional[List[OrderItemResponse]] = []
    total: float

    class Config:
        from_attributes = True

class OrderLocationUpdate(BaseModel):
    destination_latitude: Optional[float] = None
    destination_longitude: Optional[float] = None
