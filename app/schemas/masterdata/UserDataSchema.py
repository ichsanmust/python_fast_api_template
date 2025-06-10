from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime

# ===============================
# 🟢 SCHEMA UNTUK INPUT (Create, Update)
# ===============================


class Base(BaseModel):
    username: str = Field(..., min_length=6, max_length=100)
    email: EmailStr
    active: int = 1  # default active


class Create(Base):
    password: str = Field(..., min_length=6)


class Update(BaseModel):
    username: Optional[str] = Field(None, min_length=6, max_length=100)
    email: Optional[EmailStr]
    password: Optional[str] = Field(None, min_length=6)
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
    sorting: Optional[Dict[str, str]] = None  # e.g. {"created_date": "desc", "username": "asc"}
    # search: Optional[str] = None
    # start_date: Optional[datetime] = None
    # end_date: Optional[datetime] = None
    page: int = 1
    per_page: int = 10
