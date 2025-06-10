from pydantic import BaseModel

class CartBase(BaseModel):
    product_id: int
    price: int  # Store price at the time of adding to cart
    quantity: int

class CartCreate(CartBase):
    pass

class CartUpdate(BaseModel):
    quantity: int

class CartResponse(CartBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
