from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    supplier_id: int
    image: Optional[str] = None  # Stores image filename or path
    category_name: Optional[str] = None
    price: float
    stock: int


class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    supplier_id: Optional[int] = None
    category_id: Optional[int] = None
    price: Optional[float] = None
    stock: Optional[int] = None

class ProductRead(ProductBase):
    id: int

    class Config:
        from_attributes = True
