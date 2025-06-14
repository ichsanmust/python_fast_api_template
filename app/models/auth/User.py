from sqlalchemy import Column, Integer, String
from app.core import database


class User(database.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    active = Column(Integer, nullable=False)
