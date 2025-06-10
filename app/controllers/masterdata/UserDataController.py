from sqlalchemy.orm import Session
from app.models.masterdata.UserData import UserData
from app.schemas.masterdata import UserDataSchema
from passlib.context import CryptContext
from app.core import config, security
from fastapi import APIRouter, Body, Depends, HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def findByPK(db: Session, user_id: int):
    return db.query(UserData).filter(UserData.id == user_id).first()


def findByAttribute(db: Session, field: str, value: any):
    return db.query(UserData).filter(getattr(UserData, field) == value).first()


def findByAttributeOnUpdate(db: Session, field: str, value: any, id: int):
    return db.query(UserData).filter(getattr(UserData, field) == value, UserData.id != id).first()


def findAll(db: Session, skip: int = 0, limit: int = 10):
    return db.query(UserData).offset(skip).limit(limit).all()


def create(db: Session, user: UserDataSchema.Create, user_id):
    hashed_password = hash_password(user.password)
    db_user = UserData(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        active=user.active,
        created_by=user_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update(db: Session, db_user, user: UserDataSchema.Update, user_id):
    if user.username:
        db_user.username = user.username
    if user.email:
        db_user.email = user.email
    if user.password:
        db_user.hashed_password = pwd_context.hash(user.password)
    if user.active is not None:
        db_user.active = user.active
    db_user.updated_by = user_id
    db.commit()
    db.refresh(db_user)
    return db_user


def delete(db: Session, db_user):
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
