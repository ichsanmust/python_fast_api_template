from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime


# ===============================
# 🟡 SCHEMA UNTUK OUTPUT (GET Response)
# ===============================

class Out(BaseModel):
    id: int
    nama: str
    alamat: str
    umur: int
    tanggal_lahir: Optional[datetime]
    # created_date: Optional[datetime]

    class Config:
        # orm_mode = True
        from_attributes = True  # Pydantic v2 (ganti yang sesuai versi)


class Paginated(BaseModel):
    upload_data: List[Out]
    total: int
    page: int
    per_page: int

    class Config:
        # orm_mode = True
        from_attributes = True  # Pydantic v2 (ganti yang sesuai versi)


class SearchRequest(BaseModel):
    filters: Optional[Dict[str, str]] = None
    # e.g. {"created_date": "desc", "username": "asc"}
    sorting: Optional[Dict[str, str]] = None
    page: int = Field(1, example=1)
    per_page: int = Field(10, example=10)
