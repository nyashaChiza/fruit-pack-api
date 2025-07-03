from pydantic import BaseModel
from typing import List, Literal
from .order import OrderItemCreate 

class CartBase(BaseModel):
    product_id: int
    user_id: int
    price: int  # Store price at the time of adding to cart
    status: str  # e.g., "active", "purchased", "removed"
    quantity: int
    created: str  # ISO format date string

class CartCreate(CartBase):
    pass

class CartUpdate(BaseModel):
    quantity: int

class CartResponse(CartBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class CartItem(BaseModel):
    id: int
    name: str
    price: float  # price per item
    quantity: int


class CheckoutRequest(BaseModel):
    items: List[OrderItemCreate]
    full_name: str
    address: str
    latitude: float
    longitude: float
    phone: str
    payment_method: Literal["card", "cash", "paypal"]



