from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth import UserSchema
from app.controllers.auth import AuthController
from app.core import config, database, security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated

router = APIRouter()


@router.post("/signup", summary="Sign Up", description="Create New User")
def signup(
        user: UserSchema.UserCreate = Body(..., example={
            "username": "johndoe123",
            "email": "johndoe@example.com",
            "password": "securepassword"
        }),
        db: Session = Depends(database.get_db)
):

    if AuthController.get_user_by_username(db, user.username):
        return config.response_format(400, "failed", "Username already exists")
    if AuthController.get_user_by_email(db, user.email):
        return config.response_format(400, "failed", "Email already exists")

    inserted_user = AuthController.create_user(db, user)
    return config.response_format(200, "success", f"username : {user.username} has been registered", inserted_user)


# @router.post("/login", summary="Login", description="Login with username and password, so retreive token Bearer")
# def login(
#         user: UserSchema.UserLogin = Body(..., example={
#             "username": "username123",
#             "password": "password123"
#         }),
#         db: Session = Depends(database.get_db)
# ):

#     db_user = AuthController.get_user_by_username(db, user.username)
#     if not db_user or not AuthController.verify_password(user.password, db_user.hashed_password):
#         return config.response_format(400, "failed", "Invalid credentials")

#     access_token = security.create_access_token({
#         "sub": db_user.username,
#         "user_id": db_user.id
#     })
#     data = {
#         "access_token": access_token,
#         "token_type": "bearer"
#     }

#     return config.response_format(200, "success", "Success Login ", data)

@router.post("/login", summary="Login", description="Login with username and password, so retreive token Bearer")
def login(
        user: UserSchema.UserLogin,
        db: Session = Depends(database.get_db)
):

    db_user = AuthController.get_user_by_username(db, user.username)
    if not db_user:
        return config.response_format(400, "failed", "User credentials not found")
        # raise HTTPException(status_code=400, detail="Incorrect username or password") #pake ini juga bisa
    if not AuthController.verify_password(user.password, db_user.hashed_password):
        return config.response_format(400, "failed", "Wrong Password credentials")
    if not AuthController.verify_active(1, db_user.active):
        return config.response_format(400, "failed", "User Not Active")

    access_token = security.create_access_token({
        "sub": db_user.username,
        "user_id": db_user.id
    })
    data = {
        "access_token": access_token,
        "token_type": "bearer"
    }

    return config.response_format(200, "success", "Success Login ", data)


@router.get("/profile", summary="Get current user",  description="Get User Login With Token Bearier")
def read_profile(user_login: dict = Depends(security.get_current_user)):
    user_id = user_login.get("user_id")
    return config.response_format(200, "success", "You are logged in", {"user": user_login})


# @router.post("/token")
# async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(database.get_db)):
#     # print(form_data.username)

#     db_user = AuthController.get_user_by_username(db, form_data.username)
#     if not db_user or not AuthController.verify_password(form_data.password, db_user.hashed_password):
#         raise HTTPException(
#             status_code=400, detail="Incorrect username or password")

#     access_token = security.create_access_token({
#         "sub": db_user.username,
#         "user_id": db_user.id
#     })
#     data = {
#         "access_token": access_token,
#         "token_type": "bearer"
#     }

#     return data


# @router.post("/login-with-detail", summary="Login With Detail Message", description="Retrieve a list of Message Of Success or Failed.")
# def loginWithDetail(user: UserSchema.UserLogin, db: Session = Depends(database.get_db)):
#     db_user = AuthController.get_user_by_username(db, user.username)
#     if not db_user:
#         return config.response_format(400, "failed", "User credentials not found")
#     if not AuthController.verify_password(user.password, db_user.hashed_password):
#         return config.response_format(400, "failed", "Wrong Password credentials")

#     access_token = security.create_access_token(data={"sub": user.username})
#     data = {
#         "access_token": access_token,
#         "token_type": "bearer"
#     }
#     return config.response_format(200, "success", "Success Login", data)


# @router.get("/verify-token", summary="Test Verify Bearer", description="Test Verify Bearer")
# def verify(token: str):
#     return security.verify_token(token)
