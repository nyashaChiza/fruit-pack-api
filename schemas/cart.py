from pydantic import BaseModel

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
