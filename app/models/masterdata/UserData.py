from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from app.core.database import Base

class UserData(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # ← Tambahkan ini

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    active = Column(Integer, nullable=False)
    created_date = Column(TIMESTAMP, server_default=func.now())
    updated_date = Column(TIMESTAMP, onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
