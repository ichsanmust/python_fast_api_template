from typing import List, Dict, Union, Any
from fastapi.responses import JSONResponse
from zoneinfo import ZoneInfo  # Gunakan pytz kalau Python < 3.9
from fastapi.encoders import jsonable_encoder

TIMEZONE = ZoneInfo("Asia/Jakarta")  # Konstanta global
APPTITLE = "Python Fast API"
APPVERSION = "1.0.0"
APPDESCRIPTION = "Python Fast API"

# exclude from authorized bearer
excluded_endpoints = {
    ("GET", "/docs"),
    ("GET", "/openapi.json"),
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
