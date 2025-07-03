# filepath: c:\Users\usar\fruit-pack-api\schemas\user.py
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    is_active: bool
    role: str = "customer"  # Default role can be overridden

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True