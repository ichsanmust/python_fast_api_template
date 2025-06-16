from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=6,
                          max_length=100, example="username123")
    email: EmailStr = Field(..., example="user123@example.com")
    # email: EmailStr
    password: str = Field(..., min_length=6, example="password123")


class UserLogin(BaseModel):
    username: str = Field(..., min_length=6,
                          max_length=100, example="username123")
    password: str = Field(..., min_length=6, example="password123")


class Out(BaseModel):
    # id: int
    username: str
    email: EmailStr
    # active: int
    created_date: Optional[datetime] = None

    class Config:
        # orm_mode = True
        from_attributes = True  # Pydantic v2 (ganti yang sesuai versi)


class OutLogin(BaseModel):
    access_token: str
    token_type: str

    class Config:
        # orm_mode = True
        from_attributes = True  # Pydantic v2 (ganti yang sesuai versi)


class UserInfo(BaseModel):
    sub: str
    user_id: int
    exp: int
    
class SignedUser(BaseModel):
    user: Optional[UserInfo] = None
