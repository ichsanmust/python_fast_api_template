from datetime import datetime, timedelta
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from app.core import config
from fastapi import HTTPException, status
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        return config.response_format(status.HTTP_401_UNAUTHORIZED, "failed", "Token expired", {"Authenticate": "Bearer Expired"})
    except JWTError as e:
        return config.response_format(status.HTTP_401_UNAUTHORIZED, "failed", f"Invalid token: {str(e)}", {"Authenticate": "Bearer Invalid"})


async def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)
