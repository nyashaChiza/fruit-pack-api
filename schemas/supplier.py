from typing import Optional
from pydantic import BaseModel

class SupplierBase(BaseModel):
    name: str
    contact_email: str
    phone_number: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    pass

class Supplier(SupplierBase):
    id: int

    class Config:
        orm_mode = True