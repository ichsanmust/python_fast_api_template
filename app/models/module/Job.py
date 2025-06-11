from app.core.database import Base
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, func


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255))
    status = Column(Enum("pending", "processing", "completed", "failed"), default="pending")
    total_rows = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)
    error = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    processing_message = Column(String(255))
    