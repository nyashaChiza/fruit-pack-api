# filepath: c:\Users\usar\fruit-pack-api\schemas\user.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    is_active: bool
    role: str = "customer"  # Default role can be overridden
    push_token: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True

class PushTokenPayload(BaseModel):
    pushToken: str

