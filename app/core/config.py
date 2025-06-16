from pydantic import BaseModel
from typing import Generic, TypeVar
from typing import List, Dict, Union, Any, Optional
from fastapi.responses import JSONResponse
from zoneinfo import ZoneInfo  # Gunakan pytz kalau Python < 3.9
from fastapi.encoders import jsonable_encoder

TIMEZONE = ZoneInfo("Asia/Jakarta")  # Konstanta global
APPTITLE = "Python Fast API"
APPVERSION = "1.0.0"
APPDESCRIPTION = "Python Fast API"

# exclude from authorized bearer
excluded_endpoints = {
    ("GET", "/openapi.json"),

    # ("GET", "/docs"),
    # ("GET", "/redoc"),

    ("GET", "/static/rapidoc/rapidoc-min.js"),
    ("GET", "/rapidoc"),

    ("GET", "/"),
    ("POST", "/auth/signup"),
    ("GET", "/auth/signup"),
    ("POST", "/auth/login"),
    ("GET", "/auth/login"),

    # ("POST", "/auth/token"),
    # ("POST", "/auth/login-with-detail"),
    # ("POST", "/auth/verify-token"),
}


def is_excluded(method: str, path: str) -> bool:
    for m, p in excluded_endpoints:
        if method == m and (path == p or path.startswith(p + "/")):
            return True
    return False


def response_format(
    code: int,
    status: str,
    message: str,
    data: Union[Dict, List, None, Any] = None,
    exclude_unset: bool = True,
    exclude_none: bool = True,
):
    encoded_data = jsonable_encoder(
        data,
        exclude_unset=exclude_unset,
        exclude_none=exclude_none,
    )
    return JSONResponse(
        status_code=code,
        content={
            "code": code,
            "status": status,
            "message": message,
            "data": encoded_data,
        },
    )


T = TypeVar("T")
class SingleDataResponseModel(BaseModel, Generic[T]):
    code: int = 200
    status: str = 'success'
    message: str
    data: Optional[T] = None

class MultiDataResponseModel(BaseModel, Generic[T]):
    code: int = 200
    status: str = 'success'
    message: str
    data: Optional[Union[T, List[T]]] = None

class BadRequestResponseModel(BaseModel, Generic[T]):
    code: int = 400
    status: str = 'failed'
    message: str
    data: Optional[Union[T, List[T]]] = None

class ErrorDetail(BaseModel):
    loc: List[str]
    msg: str
    type: str

class ValidationErrorResponseModel(BaseModel):
    code: int = 422
    status: str = "failed"
    message: str = "Failed Input Validation"
    data: Optional[List[ErrorDetail]] = None
