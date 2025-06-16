from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime

# ===============================
# 🟢 SCHEMA UNTUK INPUT (Create, Update)
# ===============================


class Base(BaseModel):
    username: str = Field(..., min_length=6,
                          max_length=100, example="username123")
    email: EmailStr
    active: int = Field(..., example=1)


class Create(Base):
    password: str = Field(..., min_length=6, example="password123")


class Update(BaseModel):
    username: str = Field(
        None, min_length=6, max_length=100, example="username123")
    email: Optional[EmailStr] = Field(None, example="user@example.com")
    password: Optional[str] = Field(None, min_length=6, example="password123")
    active: Optional[int]


# ===============================
# 🟡 SCHEMA UNTUK OUTPUT (GET Response)
# ===============================

class Out(BaseModel):
    id: int
    username: str
    email: EmailStr
    active: int
    created_date: Optional[datetime]
    updated_date: Optional[datetime]

    class Config:
        # orm_mode = True
        from_attributes = True  # Pydantic v2 (ganti yang sesuai versi)


class Paginated(BaseModel):
    user_data: List[Out]
    total: int
    page: int
    per_page: int


class SearchRequest(BaseModel):
    filters: Optional[Dict[str, str]] = None
    # e.g. {"created_date": "desc", "username": "asc"}
    sorting: Optional[Dict[str, str]] = None
    # search: Optional[str] = None
    # start_date: Optional[datetime] = None
    # end_date: Optional[datetime] = None
    page: int = Field(1, example=1)
    per_page: int = Field(10, example=10)

class OutDeleted(BaseModel):
    message: str

    class Config:
        # orm_mode = True
        from_attributes = True  # Pydantic v2 (ganti yang sesuai versi)