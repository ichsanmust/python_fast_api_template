from sqlalchemy.orm import Session
from app.models.auth.User import User
from app.schemas.auth import UserSchema
from passlib.context import CryptContext
from app.core import security

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserSchema.UserCreate):
    hashed_password = hash_password(user.password)
    active = 1
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        active=active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def verify_active(db_active: int, user_active: int) -> bool:
    return db_active == user_active
