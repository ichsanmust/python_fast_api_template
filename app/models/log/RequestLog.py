from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.core import database
from datetime import datetime
from app.core import config


class RequestLog(database.Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    method = Column(String(10))
    path = Column(String(255))
    status_code = Column(String(10))
    process_time = Column(Float)
    timestamp = Column(DateTime, default=datetime.now(config.TIMEZONE))
    request = Column(Text)
    response = Column(Text)
