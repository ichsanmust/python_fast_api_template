from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime


class Out(BaseModel):
    message: str
    job_id: int

    class Config:
        # orm_mode = True
        from_attributes = True  # Pydantic v2 (ganti yang sesuai versi)


class OutProgress(BaseModel):

    status: str
    processing_message: str
    progress: int
    processed: int
    total: int
    processing_time_string: str
    processing_time_second : int

    class Config:
        # orm_mode = True
        from_attributes = True  # Pydantic v2 (ganti yang sesuai versi)
