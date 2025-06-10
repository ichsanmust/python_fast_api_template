from app.core.database import Base
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, func


class UploadData(Base):
    __tablename__ = "upload_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nama = Column(Text)
    alamat = Column(Text)
    umur = Column(Integer)
    tanggal_lahir = Column(DateTime)
    created_date = Column(DateTime, server_default=func.now())
