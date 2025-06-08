from pydantic import BaseModel
from typing import Optional

class CategoryBase(BaseModel):
    name: str
    icon: Optional[str] = None  # Optional icon field for category


class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int


    class Config:
        orm_mode = True
