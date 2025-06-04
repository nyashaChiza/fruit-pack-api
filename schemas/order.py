from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

# Assuming these are defined somewhere
# from .models import Order as OrderModel, Product as ProductModel
# from .database import get_db

class OrderBase(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderCreate(OrderBase):
    pass

class OrderUpdate(OrderBase):
    status: Optional[str] = None

class Order(OrderBase):
    id: int
    status: str

    class Config:
        orm_mode = True

class OrderResponse(OrderBase):
    product_name: Optional[str] = None


class SupplierBase(BaseModel):
    name: str
    contact_info: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class Supplier(SupplierBase):
    id: int

    class Config:
        orm_mode = True